#!/usr/bin/env python
'''Provision Static Routes'''
#
# Copyright (c) 2013 Juniper Networks, Inc. All rights reserved.
#

__version__ = '1.0'

import re
import sys
import time
import os.path
import logging
import platform
import argparse
import socket
import struct
import subprocess
from netaddr import IPNetwork
from tempfile import NamedTemporaryFile
from distutils.version import LooseVersion

logging.basicConfig(format='%(asctime)-15s:: %(funcName)s:%(levelname)s:: %(message)s',
                    level=logging.INFO)
log = logging.getLogger(__name__)
(PLATFORM, VERSION, EXTRA) = platform.linux_distribution()

class StaticRoute(object):
    '''Base class containing common methods for configuring static routes
    '''
    def __init__(self, **kwargs):
        self.device = kwargs['device']
        self.netw   = kwargs.get('network', [])
        self.gw     = kwargs.get('gw', [])
        self.mask   = kwargs.get('netmask', [])
        self.vlan   = kwargs.get('vlan', None)
        self.cmd    = []
        self.tempfile = NamedTemporaryFile(delete=False)
        self.config_route_list = []

    def write_network_script(self):
        '''Create an interface config file in network-scripts with given
            config
        '''
        if os.path.isfile(self.nwfile):
            tmpfile = os.path.join(os.path.dirname(self.nwfile),
                                  'moved-%s' %os.path.basename(self.nwfile))
            log.info('Backup existing file %s to %s' %(self.nwfile, tmpfile))
            os.system('sudo cp %s %s'%(self.nwfile, tmpfile))
        # read existing file
        with open(self.tempfile.name, 'w') as fd:
            fd.write('\n'.join(self.cmd))
            fd.write('\n')
        os.system('sudo cp -f %s %s'%(self.tempfile.name, self.nwfile))

    def restart_service(self):
        '''Restart network service'''
        log.info('Restarting Network Services...')
        os.system('sudo service network restart')
        time.sleep(3)
 
    def pre_config(self):
        '''Setup env before static route configuration'''
        if self.vlan:
            self.device += "."+self.vlan
        self.nwfile = os.path.join(os.path.sep, 'etc', 'sysconfig',
                                  'network-scripts', 'route-%s' %self.device)
        i = 0
        for destination in self.netw:
            prefix = IPNetwork('%s/%s' %(destination, self.mask[i])).prefixlen
            self.cmd += ['%s/%s via %s dev %s' %(
                       destination, prefix, self.gw[i], self.device)]
            self.config_route_list.append('%s %s %s' %(destination, self.mask[i], self.gw[i]))
            i+=1

    def verify_route(self):
        '''verify configured static routes'''
        actual_list = []
        for route in open('/proc/net/route', 'r').readlines():
            if route.startswith(self.device):
                route_fields = route.split()
                flags = int(route_fields[3], 16)
                destination = socket.inet_ntoa(struct.pack('I', int(route_fields[1], 16)))
                if flags & 0x2:
                    gateway = socket.inet_ntoa(struct.pack('I', int(route_fields[2], 16)))
                    mask = socket.inet_ntoa(struct.pack('I', int(route_fields[7], 16)))
                    actual_list.append('%s %s %s' %(destination, mask, gateway))
        if (set(actual_list).intersection(self.config_route_list)) != set(self.config_route_list):
            raise RuntimeError('Seems Routes are not properly configured')

    def post_config(self):
        '''Execute commands after static route configuration'''
        self.restart_service()
        self.verify_route()

    def setup(self):
        '''High level method to call individual methods to configure
            static routes
        '''
        self.pre_config()
        self.write_network_script()
        self.post_config()
        os.unlink(self.tempfile.name)

class UbuntuStaticRoute(StaticRoute):
    '''Configure Static Route in Ubuntu'''

    def restart_service(self):
        '''Restart network service for Ubuntu'''
        log.info('Restarting Network Services...')
        if LooseVersion(VERSION) < LooseVersion("14.04"):
            subprocess.call('sudo /etc/init.d/networking restart', shell=True)
        else:
            subprocess.call('sudo ifdown -a && sudo ifup -a', shell=True)
        time.sleep(5)

    def write_network_script(self):
        '''Add route to ifup-parts dir and set the correct permission'''
        if os.path.isfile(self.nwfile):
            tmpfile = os.path.join(os.path.join(os.path.sep, 'tmp'),
                                  'moved-%s' %os.path.basename(self.nwfile))
            log.info('Backup existing file %s to %s' %(self.nwfile, tmpfile))
            os.system('sudo cp %s %s'%(self.nwfile, tmpfile))
        # read existing file
        with open(self.tempfile.name, 'w') as fd:
            fd.write('#!/bin/bash\n[ "$IFACE" != "%s" ] && exit 0\n' %self.device)
            fd.write('\n'.join(self.cmd))
            fd.write('\n')
        os.system('sudo cp -f %s %s'%(self.tempfile.name, self.nwfile))
        os.system('sudo chmod 755 %s'%(self.nwfile))
        with open(self.tempfile.name, 'w') as fd:
            fd.write('#!/bin/bash\n[ "$IFACE" != "%s" ] && exit 0\n' %self.device)
            fd.write('\n'.join(self.downcmd))
            fd.write('\n')
        os.system('sudo cp -f %s %s'%(self.tempfile.name, self.downfile))
        os.system('sudo chmod 755 %s'%(self.downfile))

    def pre_config(self):
        '''Setup env before static route configuration in Ubuntu'''
        # Any changes to the file/logic with static routes has to be
        # reflected in setup.py too
        if self.vlan:
            self.device = 'vlan'+self.vlan
        i = 0
        for destination in self.netw:
            prefix = IPNetwork('%s/%s' %(destination, self.mask[i])).prefixlen
            self.cmd += ['%s/%s via %s dev %s' %(
                       destination, prefix, self.gw[i], self.device)]
            self.config_route_list.append('%s %s %s' %(destination, self.mask[i], self.gw[i]))
            i+=1
        self.downfile = os.path.join(os.path.sep, 'etc', 'network', 'if-down.d', 'routes')
        self.downcmd = ['ip route del '+x for x in self.cmd]
        self.nwfile = os.path.join(os.path.sep, 'etc', 'network', 'if-up.d', 'routes')
        self.cmd = ['ip route add '+x for x in self.cmd]

def parse_cli(args):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', '-v',
                        action='version',
                        version=__version__,
                        help='Display version and exit')
    parser.add_argument('--device',
                        action='store',
                        help='Interface Name')
    parser.add_argument('--network',
                        action='store',
                        default=[],
                        nargs='+',
                        metavar='DESTINATION',
                        help='Network address of the Static route')
    parser.add_argument('--netmask',
                        action='store',
                        default=[],
                        nargs='+',
                        metavar='NETMASK',
                        help='Netmask of the Static route')
    parser.add_argument('--gw',
                        action='store',
                        default=[],
                        nargs='+',
                        metavar='GATEWAY',
                        help='Gateway Address of the Static route')
    parser.add_argument('--vlan',
                        action='store',
                        help='vLAN ID')
    pargs = parser.parse_args(args)
    if len(args) == 0:
        parser.print_help()
        sys.exit(2)
    return dict(pargs._get_kwargs())
    
def main():
    pargs = parse_cli(sys.argv[1:])
    if PLATFORM.lower() != 'ubuntu':
        route = StaticRoute(**pargs)
    else:
        route = UbuntuStaticRoute(**pargs)
    route.setup()

if __name__ == '__main__':
    main()
