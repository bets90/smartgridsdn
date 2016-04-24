#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Host, RemoteController
from mininet.node import OVSKernelSwitch
from mininet.log import setLogLevel, info
from lib.controller import POXBridge as AmiController
from mininet.cli import CLI


def AMINetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info('*** Adding controller \n')
    c1 = net.addController('c1',
                           controller=AmiController,
                           #protocol='tcp',
                           port=6635)
    c2 = RemoteController('c2', ip='127.0.0.1', port=6633)
    #net.addController(c2)

    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.10', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.20', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.30', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.31', defaultRoute=None)

    info('*** Add links\n')
    net.addLink(h1, s1)
    net.addLink(s1, s2)
    net.addLink(h2, s2)
    net.addLink(s2, s3)
    net.addLink(h3, s3)
    net.addLink(h4, s3)
    
    info( '*** Starting network\n')
    net.build()
    # info ('*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    # info('*** Starting switches\n')
    net.get('s1').start([c1])
    net.get('s3').start([c1])
    net.get('s2').start([c1])

    info('*** Post configure switches and hosts\n')
    #net.pingAll()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    AMINetwork()
