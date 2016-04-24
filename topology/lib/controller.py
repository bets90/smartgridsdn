#!/usr/bin/python
from mininet.net import Mininet
from mininet.node import Controller
from mininet.topo import SingleSwitchTopo
from mininet.log import setLogLevel
from os import environ

POXDIR = environ[ 'HOME' ] + '/pox'


class POXBridge(Controller):
    """Custom Controller class to invoke POX forwarding.l2_learning"""

    def __init__(self, name, cdir=POXDIR,
                 command='python pox.py',
                 cargs=('openflow.of_01 --port=%s '
                        'forwarding.l2_learning'),
                 **kwargs):
        Controller.__init__(self, name, cdir=cdir,
                    command=command,
                    cargs=cargs, **kwargs)
        for key in kwargs:
            print "another keyword arg: %s: %s" % (key, kwargs[key])

controllers = {'poxbridge': POXBridge}


if __name__ == '__main__':
    '''Test code to run controller'''
    setLogLevel( 'info' )
    net = Mininet( topo=SingleSwitchTopo(2))
    net.addController(POXBridge)
    c1.start()
    net.start()
    net.pingAll()
    net.stop()
