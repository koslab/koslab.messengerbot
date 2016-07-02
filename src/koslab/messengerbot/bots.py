from koslab.messengerbot.request import Response
from koslab.messengerbot.logger import logger
from kombu import Connection, Exchange, Queue
from multiprocessing import Process, Pool
import json

__all__ = ['Bots', 'KombuBots']

def spawn_bot(bot_class, bot_args, event):
    bot = bot_class(**bot_args)
    bot.handle_event(event)

def spawn_bot_amqp(bot_class, bot_args, event, message):
    bot = bot_class(**bot_args)
    bot.handle_event(event)
    message.ack()

class Bots(object):
    '''
    :param: validation_token: hub validation token
    :param: page_bots: a dictionary of page id and MessengerBot implementation
    '''
    def __init__(self, validation_token, page_bots):
        self.validation_token = validation_token
        self.page_bots = page_bots

    def webhook(self, request):
        if request.method == 'GET':
            return self.webhook_get(request)
        if request.method == 'POST':
            return self.webhook_post(request)

    def webhook_get(self, request):
        if (request.get('hub.mode') == 'subscribe' and 
            request.get('hub.verify_token') == self.validation_token):
            logger.info('Received hub challenge')
            return Response(body=request.get('hub.challenge'), status=200)
        else:
            logger.info('Invalid hub challenge')
            return Response(status=403)

    def webhook_post(self, request):
        data = json.loads(request.body)

        if (data['object'] == 'page'):
            for entry in data['entry']:
                page_id = entry['id']
                timestamp = entry['time']
                bot_class, bot_args = self.get_bot(page_id)
                for event in entry['messaging']:
                    Process(target=spawn_bot, 
                            args=(bot_class, bot_args, event)).start()

        return Response(status=200)

    def get_bot(self, page_id):
        bot = self.page_bots.get(page_id, None)
        if bot is None:
            raise ValueError('Unable to select bot for page %s ' % page_id)
        return bot

    def init_bots(self):
        for page_id, (bot_class, bot_args) in self.page_bots.items():
            print "Configuring %s for PageID:%s" % (
                    bot_class.__name__, page_id)
            bot = bot_class(**bot_args)
            bot.configure()

    def initialize(self):
        self.init_bots()

class KombuBots(Bots):
    '''
    Web hook for Kombu queue

    :param: validation_token: hub validation token
    '''
    def __init__(self, validation_token, page_bots, transport, exchange=None, queue=None):
        super(KombuBots, self).__init__(validation_token, page_bots)
        self.page_bots = page_bots
        self.transport = transport
        if exchange is None:
            exchange = Exchange('MessengerBot', 'direct', durable=True)
        self.exchange = exchange
        if queue is None:
            queue = Queue('messages', exchange=exchange, routing_key='messages')
        self.queue = queue

    def webhook_post(self, request):
        data = json.loads(request.body)
        if (data['object'] == 'page'):
            for entry in data['entry']:
                page_id = entry['id']
                timestamp = entry['time']
                self.queue_events(entry['messaging'])
        return Response(status=200)

    def queue_events(self, events):
        with Connection(self.transport) as conn:
            producer = conn.Producer(serializer='json')
            for event in events:
                producer.publish(event, exchange=self.exchange, 
                        routing_key=self.queue.routing_key,
                        declare=[self.queue])

    def consume(self):
        def worker(event, message):
            page_id = event['recipient']['id']
            bot_class, bot_args = self.get_bot(page_id)
            p = Process(target=spawn_bot_amqp, args=(bot_class, bot_args, event,
                message))
            p.start()

        with Connection(self.transport) as conn:
            with conn.Consumer(self.queue, callbacks=[worker]) as consumer:
                while True:
                    conn.drain_events()

    def initialize(self):
        super(KombuBots, self).init_bots()
        print "Running %s Kombu consumer" % self
        p = Process(target=self.consume)
        p.start()
