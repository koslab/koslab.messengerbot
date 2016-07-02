from koslab.messengerbot.request import Response
from koslab.messengerbot.logger import logger
import json

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
            if (request.get('hub.mode') == 'subscribe' and 
                request.get('hub.verify_token') == self.validation_token):
                logger.info('Received hub challenge')
                return Response(body=request.get('hub.challenge'), status=200)
            else:
                logger.info('Invalid hub challenge')
                return Response(status=403)

        if request.method == 'POST':
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
