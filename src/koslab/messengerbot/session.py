from beaker.cache import CacheManager

class SessionManager(object):

    def __init__(self, type='memory', **kwargs):
        opts = kwargs or {
            'data_dir': '/tmp/messengerbot-cache/data',
            'lock_dir': '/tmp/messengerbot-cache/lock'
        }
        opts['type'] = type
        self.cachemgr = CacheManager(**opts)

    def get_session(self, event):
        ns = '.'.join([event['recipient']['id'],event['sender']['id']])
        cache = self.cachemgr.get_cache(ns)
        return Session(cache)

_marker = []

class Session(object):

    def __init__(self, cache):
        self.cache = cache

    def get(self, key, default=_marker):
        if default is not _marker:
            value = self.cache._get_value(key)
            if not value.has_current_value():
                return default
        return self.cache.get(key=key)

    def set(self, key, value):
        self.cache.set_value(key, value)

    def delete(self, key):
        self.cache.remove_value(key=key)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.set(key, value)

    def __delitem__(self, key):
        return self.delete(key)
