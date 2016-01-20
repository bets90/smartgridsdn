from mininet.topo import Topo
from mininet.net import Mininet
from topology import  AMITopology
from mininet.log import setLogLevel, info

def testNetwork():
    "test sample network created"
    topo = AMITopology()
    net = Mininet(topo)
    print "Starting Network"
    net.start()
    #net.pingAll()
    net.stop()

if __name__=='__main__':
    setLogLevel('info')
    testNetwork()
