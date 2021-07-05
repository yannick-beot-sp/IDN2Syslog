# encoding = utf-8

import os
import sys
import time
import datetime
from requests.exceptions import HTTPError
import json
import re
from builtins import object
import logging
import logging.handlers
import IStore
import socket


from Helper import Helper
from IDNClient import IDNClient
from StoreFactory import StoreFactory

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


syslog_server_address = os.getenv("SYSLOG_HOST")
syslog_server_port = int(os.getenv("SYSLOG_PORT") or '514')
syslog_server_soctype_str = os.getenv("SYSLOG_SOCKET_TYPE") or 'UDP'
if syslog_server_soctype_str == 'UDP':
    syslog_server_soctype = socket.SOCK_DGRAM
else:
    syslog_server_soctype = socket.SOCK_STREAM

client_id = os.getenv("IDN_CLIENT_ID")
client_secret = os.getenv("IDN_CLIENT_SECRET")
org_name = os.getenv("IDN_TENANT")

sysLogger = logging.getLogger('QRADARSYSLOG')
sysLogger.setLevel(logging.INFO)
syslog_handler = logging.handlers.SysLogHandler(address=(
    syslog_server_address, syslog_server_port), facility=logging.handlers.SysLogHandler.LOG_LOCAL1, socktype=syslog_server_soctype)
sysLogger.addHandler(syslog_handler)


def use_now(now, old)->bool:
    """This method will determine if the current timestamp should be used instead of the value stored in the checkpoint file.
     Will return 'false' if the checkpoint time is 1 or more days in the past"""

    try:
        now_dt = datetime.datetime.strptime(now, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        now_dt = datetime.datetime.strptime(now, '%Y-%m-%dT%H:%M:%SZ')

    try:
        old_dt = datetime.datetime.strptime(old, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        old_dt = datetime.datetime.strptime(old, '%Y-%m-%dT%H:%M:%SZ')

    diff = old_dt - now_dt
    delta_days = diff.days

    if(int(delta_days) > 1):
        ret = True

    return False


def collect_events(helper: Helper, client: IDNClient, store: IStore):

    # Read the timestamp from the checkpoint variable in AWS System Manager Parameter Store
    # - The checkpoint contains the ISO datetime of the 'created' field of the last event seen in the
    #   previous execution of the script. If the checkpoint time was greater than a day in the past, use current datetime to avoid massive load if search disabled for long period of time

    new_checkpoint_time = (datetime.datetime.utcnow() -
                           datetime.timedelta(minutes=60)).isoformat() + "Z"
    # Set checkpoint time to either the current timestamp, or what was saved in the checkpoint

    checkpoint = None
    try:
        checkpoint = store.get_parameter('sailpoint-checkpoint')
        if use_now(new_checkpoint_time, checkpoint):
            helper.log_debug("Using new checkpoint")
            checkpoint_time = new_checkpoint_time
        else:
            helper.log_debug("Using old checkpoint")
            checkpoint_time = checkpoint

    except:
        helper.log_debug("ERROR. Using new checkpoint")
        checkpoint_time = new_checkpoint_time

    # Search API results are slightly delayed, allow for 5 minutes though in reality
    # this time will be much shorter. Cap query at checkpoint time to 5 minutes ago
    search_delay_time = (datetime.datetime.utcnow() -
                         datetime.timedelta(minutes=5)).isoformat() + "Z"

    helper.log_error(
        f'checkpoint_time {checkpoint_time} search_delay_time {search_delay_time}')
    query_checkpoint_time = checkpoint_time.replace(
        '-', '\\-').replace('.', '\\.').replace(':', '\\:')
    query_search_delay_time = search_delay_time.replace(
        '-', '\\-').replace('.', '\\.').replace(':', '\\:')

    checkpoint_time = search_delay_time

    # Search criteria - retrieve all audit events since the checkpoint time, sorted by created date
    query = f"created:>{query_checkpoint_time} AND created:<{query_search_delay_time}"

    audit_events = client.search(query)
    count = 0
    # Iterate the audit events array and create events for each one
    for audit_event in audit_events:
        # Get Latest checkpoint_time
        checkpoint_time = audit_event['created']
        sysLogger.info(json.dumps(audit_event))
        count += 1
        # print(audit_event)
    print("Sent {} events to {} {}".format(
        count, syslog_server_address, syslog_server_port))

    print("New checkpoint: {}".format(checkpoint_time))
    store.set_parameter('sailpoint-checkpoint', checkpoint_time)


if __name__ == "__main__":
    helper = Helper()
    store = StoreFactory().get_store()
    client = IDNClient(
        tenant=org_name,
        client_id=client_id,
        client_secret=client_secret,
        helper=helper
    )
    collect_events(helper, client, store)
