import requests
from koslab.messengerbot.logger import logger
import json
import re
import time
from koslab.messengerbot.session import SessionManager
from beaker.util import parse_cache_config_options
import os

class BaseMessengerBot(object):

    POSTBACK_HANDLERS = {}
    GREETING_TEXT = 'Hello World!'
    STARTUP_MESSAGE = { 'text': 'Hello World!' }
    PERSISTENT_MENU = [{
       'type': 'postback',
       'title': 'Get Started',
       'payload': 'messengerbot.get_started'
    }]


    def __init__(self, page_access_token, session_opts=None):
        self.session_opts = session_opts or {
            'type': 'file',
            'data_dir': '/tmp/messengerbot-cache/data',
            'lock_dir': '/tmp/messengerbot-cache/lock'
        }
        self.sessionmgr = SessionManager(**self.session_opts)
        self.page_access_token = page_access_token

    def start_hook(self, event):
        if self.STARTUP_MESSAGE is not None:
            self.send(event['sender'], self.STARTUP_MESSAGE)

    def authentication_hook(self, event):
        pass

    def message_hook(self, event):
        pass

    def message_delivered_hook(self, event):
        pass

    def postback_hook(self, event):
        try:
            payload = json.loads(event['postback']['payload'])
            ev = payload['event']
        except:
            ev = payload = event['postback']['payload']
        if ev == 'messengerbot.get_started':
            self.start_hook(event)
        for pyl, method in self.POSTBACK_HANDLERS.items():
            if pyl==ev or re.match(pyl, ev):
                getattr(self, method)(event)

    def read_hook(self, event):
        pass

    def account_linking_hook(self, event):
        pass

    def user_profile(self, user, fields=None):
        fields = fields or ['first_name','last_name','profile_pic','locale',
                                'timezone','gender']
        url = 'https://graph.facebook.com/v2.6/%s' % user['id']
        resp = requests.get(url, data={'fields': ','.join(fields)})
        resp_data = resp.json()
        if resp_data.get('error', None):
            return {
                'first_name': '',
                'last_name': '',
                'profile_pic': '',
                'locale': 'en_US',
                'timezone': 0,
                'gender': ''
            }
        return resp_data

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
        resp_data = resp.json()
        error = resp_data.get('error', None)
        if error and error['code'] != 2:
            # rate limit error, retry
            if error['code'] == 4:
                time.sleep(5)
                self.send(recipient, message, sender_action)
        return resp

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

    def thread_settings(self, setting):
        url = 'https://graph.facebook.com/v2.6/me/thread_settings'
        resp = requests.post('%s?access_token=%s' % (url,
                            self.page_access_token), json=setting)
        return resp

    def configure(self):
        # configure greeting
        if self.GREETING_TEXT is not None:
            self.thread_settings({
                'setting_type': 'greeting', 
                'greeting': {
                    'text': self.GREETING_TEXT
                }
            })
        # configure Get Started button
        self.thread_settings({
            'setting_type': 'call_to_actions',
            'thread_state': 'new_thread',
            'call_to_actions': [
                { 'payload': 'messengerbot.get_started' }
            ]
        })

        # configure Persistent Menu
        if self.PERSISTENT_MENU is not None:
            self.thread_settings({
                'setting_type': 'call_to_actions',
                'thread_state': 'existing_thread',
                'call_to_actions': self.PERSISTENT_MENU
            })

    def get_session(self, event):
        return self.sessionmgr.get_session(event)
