from koslab.messengerbot.request import Response
from koslab.messengerbot.logger import logger
from kombu import Connection, Exchange, Queue
from multiprocessing import Process, Pool
import json

__all__ = ['Bots', 'KombuBots']

def spawn_bot(bot_class, bot_args, event):
    bot = bot_class(**bot_args)
    bot.handle_event(event)

def spawn_bot_amqp(bot_class, bot_args, send_transport, send_exchange, send_queue, 
                    event, message):
    bot = bot_class(send_transport=send_transport, send_exchange=send_exchange, 
            send_queue=send_queue, **bot_args)
    bot.handle_event(event)
    message.ack()

def spawn_send_message_worker(event, message):
    from koslab.messengerbot.bot import send_message
    resp = send_message(**event)
    if resp.status_code == 200:
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
    def __init__(self, validation_token, page_bots, transport=None, 
                exchange=None, queue=None, send_transport=None,
                send_exchange=None, send_queue=None):
        super(KombuBots, self).__init__(validation_token, page_bots)
        self.page_bots = page_bots
        self.transport = transport or 'amqp://guest:guest@localhost:5672//'
        self.exchange = exchange or 'MessengerBot'
        self.queue = queue or 'messages'
        self.send_transport = send_transport or transport
        self.send_exchange = send_exchange or 'MessengerBot'
        self.send_queue = send_queue or 'replies'

    def webhook_post(self, request):
        data = json.loads(request.body)
        if (data['object'] == 'page'):
            for entry in data['entry']:
                page_id = entry['id']
                timestamp = entry['time']
                self.queue_events(entry['messaging'])
        return Response(status=200)

    def queue_events(self, events):
        exchange = Exchange(self.exchange, 'direct', durable=True)
        queue = Queue(self.queue, exchange=exchange, routing_key=self.queue)
        with Connection(self.transport) as conn:
            producer = conn.Producer(serializer='json')
            for event in events:
                producer.publish(event, exchange=exchange, 
                        routing_key=queue.routing_key,
                        declare=[queue])

    def consume(self):
        def worker(event, message):
            page_id = event['recipient']['id']
            bot_class, bot_args = self.get_bot(page_id)
            p = Process(target=spawn_bot_amqp, args=(bot_class, bot_args, 
                        self.transport, self.send_exchange, 
                        self.send_queue, event, message))
            p.start()

        exchange = Exchange(self.exchange, 'direct', durable=True)
        queue = Queue(self.queue, exchange=exchange, routing_key=self.queue)
        with Connection(self.transport) as conn:
            with conn.Consumer(queue, callbacks=[worker]) as consumer:
                while True:
                    conn.drain_events()

    def sender(self):
        def worker(event, message):
            p = Process(target=spawn_send_message_worker, args=(event, message))
            p.start()

        exchange = Exchange(self.send_exchange, 'direct', durable=True)
        queue = Queue(self.send_queue, exchange=exchange, 
                        routing_key=self.send_queue)
        with Connection(self.send_transport) as conn:
            with conn.Consumer(queue, callbacks=[worker]) as consumer:
                while True:
                    conn.drain_events()

    def initialize(self):
        super(KombuBots, self).init_bots()
        print "Running %s message consumer" % self
        p = Process(target=self.consume)
        p.start()
        print "Running %s message sender" % self
        p2 = Process(target=self.sender)
	p2.start()
