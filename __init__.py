# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import OpenERPSession, Root, lazy_property
import redis
from . import redis_session
from .config import redis_host, redis_port, redis_password

import logging

_logger = logging.getLogger(__name__)


def post_load_method():

    def session_gc(session_store):
        # skip cleanup of stale sessions because this done automatically by Redis expiry feature
        pass

    @lazy_property
    def session_store(self):
        # Setup http sessions
        redis_instance = redis.Redis(host=redis_host, port=redis_port, db=0, password=redis_password)
        _logger.info('Setting up sesion store on Redis server')
        return redis_session.RedisSessionStore(redis_instance, session_class=OpenERPSession)

    Root.session_store = session_store
    http.session_gc = session_gc
