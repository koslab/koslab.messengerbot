from koslab.messengerbot.request import Response
from koslab.messengerbot.logger import logger
from kombu import Connection, Exchange, Queue
from multiprocessing import Process
import json

__all__ = ['WebHook', 'AMQPWebHook']

class WebHook(object):
    '''
    :param: validation_token: hub validation token
    :param: page_bots: a dictionary of page id and MessengerBot implementation
    '''
    def __init__(self, validation_token, page_bots):
        self.validation_token = validation_token
        self.page_bots = page_bots

    def handle(self, request):
        if request.method == 'GET':
            return self.handle_get(request)
        if request.method == 'POST':
            return self.handle_post(request)

    def handle_get(self, request):
        if (request.get('hub.mode') == 'subscribe' and 
            request.get('hub.verify_token') == self.validation_token):
            logger.info('Received hub challenge')
            return Response(body=request.get('hub.challenge'), status=200)
        else:
            logger.info('Invalid hub challenge')
            return Response(status=403)

    def handle_post(self, request):
        data = json.loads(request.body)

        if (data['object'] == 'page'):
            for entry in data['entry']:
                page_id = entry['id']
                timestamp = entry['time']
                bot = self.get_bot(page_id) 
                for event in entry['messaging']:
                    bot.handle_event(event)
        return Response(status=200)

    def get_bot(self, page_id):
        bot = self.page_bots.get(page_id, None)
        if bot is None:
            raise ValueError('Unable to select bot for page %s ' % page_id)
        return bot

class AMQPWebHook(WebHook):
    '''
    Web hook for AMQP queue

    :param: validation_token: hub validation token
    '''
    def __init__(self, validation_token, page_bots, transport, exchange=None, queue=None):
        super(AMQPWebHook, self).__init__(validation_token, page_bots)
        self.page_bots = page_bots
        self.transport = transport
        if exchange is None:
            exchange = Exchange('MessengerBot', 'direct', durable=True)
        self.exchange = exchange
        if queue is None:
            queue = Queue('messages', exchange=exchange, routing_key='messages')
        self.queue = queue

    def handle_post(self, request):
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
        def spawn_bot(event, message):
            page_id = event['recipient']['id']
            bot = self.get_bot(page_id)
            bot.handle_event(event)
            message.ack()

        with Connection(self.transport) as conn:
            with conn.Consumer(self.queue, callbacks=[spawn_bot]) as consumer:
                while True:
                    conn.drain_events()

    def start_consumer(self):
        print "Running %s AMQP consumer" % self
        p = Process(target=self.consume)
        p.start()
