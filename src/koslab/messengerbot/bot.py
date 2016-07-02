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

    def delivery_confirmation_hook(self, event):
        pass

    def postback_hook(self, event):
        pass

    def read_hook(self, event):
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
