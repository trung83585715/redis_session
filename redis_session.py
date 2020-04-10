# -*- coding: utf-8 -*-

import json
import logging
from werkzeug.contrib.sessions import SessionStore

SESSION_TIMEOUT = 60 * 60 * 24  # 1 week in seconds

_logger = logging.getLogger('Redis Session')


class RedisSessionStore(SessionStore):
    """
    SessionStore that saves session to redis
    """

    def __init__(self, redis, session_class,key_template='session:%s', generate_salt=None):

        if not generate_salt:
            generate_salt = b'RFHXSYf_A@!d!2@g'  # default salt

        SessionStore.__init__(self, session_class)
        self.redis = redis
        self.key_template = key_template
        self.generate_salt = generate_salt

    def new(self):
        """Generate a new session."""
        key = self.generate_key(self.generate_salt)
        res = self.session_class({}, key , True)
        return res

    def get_session_key(self, sid):
        return self.key_template % sid.encode('utf-8')

    def save(self, session):
        key = self.get_session_key(session.sid)
        if self.redis.set(key, json.dumps(dict(session))):
            return self.redis.expire(key, SESSION_TIMEOUT) # any key not accessed in 1 week will be deleted

    def delete(self, session):
        key = self.get_session_key(session.sid)
        return self.redis.delete(key)

    def get(self, sid):
        if not self.is_valid_key(sid):
            return self.new()

        key = self.get_session_key(sid)
        saved = self.redis.get(key)
        if saved:
            data = json.loads(saved.decode("utf-8"))
            self.redis.expire(key, SESSION_TIMEOUT) # key accessed, refresh expiry to 1 week
            return self.session_class(data, sid, False)

        return self.new()

    def list(self):
        """
        Lists all sessions in the store.
        """
        session_keys = self.redis.keys(self.key_template[:-2] + '*')
        return [s[len(self.key_template) - 2:] for s in session_keys]