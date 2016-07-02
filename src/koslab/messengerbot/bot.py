import requests
from koslab.messengerbot.logger import logger
import json

class BaseMessengerBot(object):

    def __init__(self, page_access_token):
        self.page_access_token = page_access_token

    def authentication_hook(self, event):
        pass

    def message_hook(self, event):
        pass

    def message_delivered_hook(self, event):
        pass

    def postback_hook(self, event):
        pass

    def read_hook(self, event):
        pass

    def account_linking_hook(self, event):
        pass

    def send(self, recipient, message=None, sender_action=None):
        request_data = { 'recipient': recipient }
        if not (message or sender_action):
            raise ValueError('message or sender_action is required')
        if message:
            request_data['message'] = message
        elif sender_action:
            if sender_action not in ['mark_seen', 'typing_on', 'typing_off']:
                raise ValueError('Invalid Action %s' % sender_action)
            request_data['sender_action'] = sender_action

        url = 'https://graph.facebook.com/v2.6/me/messages'
        resp = requests.post('%s?access_token=%s' % (url, 
                    self.page_access_token), json=request_data)
        if resp.status_code == 200:
            data = resp.json()

    def handle_event(self, event):
        if event.get('optin', None):
            logger.debug('Authentication hook: %s' % json.dumps(event))
            self.authentication_hook(event)
        elif event.get('message', None):
            logger.debug('Message hook: %s' % json.dumps(event))
            self.message_hook(event)
        elif event.get('delivery', None):
            logger.debug('Message delivered hook: %s' % json.dumps(event))
            self.message_delivered_hook(event)
        elif event.get('postback', None):
            logger.debug('Postback hook: %s' % json.dumps(event))
            self.postback_hook(event)
        elif event.get('read', None):
            logger.debug('Read hook: %s' % json.dumps(event))
            self.read_hook(event)
        elif event.get('account_linking', None):
            logger.debug('Account linking hook: %s' % json.dumps(event))
            self.account_linking_hook(event)
        else:
            logger.info(
                'Webhook received unknown messagingEvent %s' % json.dumps(event))

