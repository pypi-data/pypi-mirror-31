"""graphennewsrpc."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import time
import json
import logging
from .exceptions import (
    UnauthorizedError, RPCConnection, RPCError, NumRetriesReached, CallRetriesReached
)

log = logging.getLogger(__name__)


def is_network_appbase_ready(props):
    """Checks if the network is appbase ready"""
    network_version = '0.0.0'
    if "STEEMIT_BLOCKCHAIN_VERSION" in props:
        network_version = props['STEEMIT_BLOCKCHAIN_VERSION']
    elif "STEEM_BLOCKCHAIN_VERSION" in props:
        network_version = props['STEEM_BLOCKCHAIN_VERSION']
    return network_version >= '0.19.4'


def get_query(appbase, request_id, api_name, name, args):
    query = []
    if not appbase:
        query = {"method": "call",
                 "params": [api_name, name, list(args)],
                 "jsonrpc": "2.0",
                 "id": request_id}
    else:
        args = json.loads(json.dumps(args))
        # print(args)
        if len(args) > 0 and isinstance(args, list) and isinstance(args[0], dict):
            query = {"method": api_name + "." + name,
                     "params": args[0],
                     "jsonrpc": "2.0",
                     "id": request_id}
        elif len(args) > 0 and isinstance(args, list) and len(args[0]) > 0 and isinstance(args[0], list) and isinstance(args[0][0], dict):
            for a in args[0]:
                query.append({"method": api_name + "." + name,
                              "params": a,
                              "jsonrpc": "2.0",
                              "id": request_id})
                request_id += 1
        elif args:
            query = {"method": "call",
                     "params": [api_name, name, list(args)],
                     "jsonrpc": "2.0",
                     "id": request_id}
            request_id += 1
        elif api_name == "condenser_api":
            query = {"method": api_name + "." + name,
                     "jsonrpc": "2.0",
                     "params": [],
                     "id": request_id}
        else:
            query = {"method": api_name + "." + name,
                     "jsonrpc": "2.0",
                     "params": {},
                     "id": request_id}
    return query


def get_api_name(appbase, *args, **kwargs):
    if not appbase:
        # Sepcify the api to talk to
        if ("api" in kwargs) and len(kwargs["api"]) > 0:
            api_name = kwargs["api"].replace("_api", "") + "_api"
        else:
            api_name = None
    else:
        # Sepcify the api to talk to
        if ("api" in kwargs) and len(kwargs["api"]) > 0:
            if kwargs["api"] != "jsonrpc":
                api_name = kwargs["api"].replace("_api", "") + "_api"
            else:
                api_name = kwargs["api"]
        else:
            api_name = "condenser_api"
    return api_name


def sleep_and_check_retries(num_retries, cnt, url, errorMsg=None, sleep=True, call_retry=False, showMsg=True):
    """Sleep and check if num_retries is reached"""
    if errorMsg:
        log.warning("Error: {}".format(errorMsg))
    if (num_retries >= 0 and cnt > num_retries):
        if not call_retry:
            raise NumRetriesReached()
        else:
            raise CallRetriesReached()
    if showMsg:
        if call_retry:
            log.warning("Retry RPC Call on node: %s (%d/%d) \n" % (url, cnt, num_retries))
        else:
            log.warning("Lost connection or internal error on node: %s (%d/%d) \n" % (url, cnt, num_retries))
    if not sleep:
        return
    if cnt < 1:
        sleeptime = 0
    elif cnt < 10:
        sleeptime = (cnt - 1) * 1.5 + 0.5
    else:
        sleeptime = 10
    if sleeptime:
        log.warning("Retrying in %d seconds\n" % sleeptime)
        time.sleep(sleeptime)
