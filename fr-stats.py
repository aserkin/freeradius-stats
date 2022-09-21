#!/usr/bin/env python3
import logging
import json
import re, os
import subprocess as sp
import datetime as dt
from logging.handlers import SysLogHandler
import tempfile
import time
import socket
#from vyos.util import chown

usage = """
Get FreeRADIUS stats per client
"""

# Read and return array with radius clients
def get_clientlist():
    command = 'radmin -e \"show client list\"'
    client_list = sp.run(command,shell=True,stdout=sp.PIPE).stdout.decode('utf-8').split()
    return client_list

# Read and return client config
def get_clientcfg(client):
    client_cfg = {}
    command = 'radmin -e \"show client config '+client+'\"'
    output = sp.run(command,shell=True,stdout=sp.PIPE).stdout.decode('utf-8').replace(' ','').split('\n')
    for item in output:
      item = re.sub('[\t{}]', '',item)
      item = re.split('[,=]',item)
      if len(item) > 1:
          client_cfg[item[0]] = item[1]
    return client_cfg

def get_authstats(client):
    cli_stats = {}
    command = 'radmin -e \"stats client auth '+client+'\"'
    output = sp.run(command,shell=True,stdout=sp.PIPE).stdout.decode('utf-8').replace(' ','').split('\n')
    for item in output:
      item = item.split()
      if len(item) > 1:
          cli_stats[item[0]] = item[1]
    return cli_stats


def main():
    hostname=socket.gethostname()
    client_dict={}
    for client in get_clientlist():
      client_dict[client] = get_clientcfg(client)
    for client in client_dict:
      client_dict[client]['stats'] = get_authstats(client)
#    print(json.dumps(client_dict,indent=2))
    for client in client_dict:
      tags = 'freeradius_stats,hostname=\"%s\",client=\"%s\"' % (hostname,client)
      try:
        if client_dict[client]['ipaddr']:
          tags = tags + ',ipaddr=\"%s\"' % client_dict[client]['ipaddr']
      except KeyError:
        if client_dict[client]['ipv6addr']:
          tags = tags + ',ipv6addr=\"%s\"' % client_dict[client]['ipv6addr']
      try:
        if client_dict[client]['shortname']:
          tags = tags + ',shortname=\"%s\"' % client_dict[client]['shortname']
      except KeyError:
        pass
      values = ""
      for parm in client_dict[client]['stats']:
        if parm == 'last_packet':
          tags = tags + "," + parm + "=" + client_dict[client]['stats'][parm] + " "
        else:
          values = values + parm + "=" + client_dict[client]['stats'][parm] + ","
      ts=int(time.time())
      print(tags + values[:-1].replace('.','_') + " " + str(ts) + "000000000")
    
if __name__ == "__main__":
    main()
