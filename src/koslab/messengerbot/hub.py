import morepath
import logging
from koslab.messengerbot.bots import Bots, KombuBots
from koslab.messengerbot.request import WebObRequestAdapter
import importlib

class App(morepath.App):

    def __init__(self, config):
        params = {
            'validation_token': config['hub_verify_token'],
            'page_bots': self.bots_config(config)
        }
        if config.get('use_message_queue', False):
            coordinator_klass = KombuBots
            params['transport'] = config.get('message_queue', None)
        else:
            coordinator_klass = Bots

        self.bots = coordinator_klass(**params)
        print("=== Configuring bots ===")
        self.bots.initialize()
        print("=== Starting up webhook on /%s ===" % config['webhook'])

    def bots_config(self, config):
        bots = config.get('bots', [])
        result = {}
        for bot in bots:
            bot_module, bot_class = bot.get('class').strip().split(':')
            m = importlib.import_module(bot_module)
            klass = getattr(m, bot_class)
            kwargs = bot.get('args', {})
            kwargs['page_access_token'] = bot['access_token']
            result[str(bot['page_id'])] = (klass, kwargs)
        return result

class Root(object):
    pass

@App.path(path='{webhook}', model=Root)
def get_root(webhook):
    config = morepath.settings().config
    if config.webhook != webhook:
        return None
    return Root()

@App.view(model=Root, name='', request_method='GET')
def webhook_get(context, request):
    req = WebObRequestAdapter(request)
    resp = request.app.bots.webhook(req)
    return morepath.Response(**resp.params())

@App.view(model=Root, name='', request_method='POST')
def webhook_post(context, request):
    req = WebObRequestAdapter(request)
    resp = request.app.bots.webhook(req)
    return morepath.Response(**resp.params())

