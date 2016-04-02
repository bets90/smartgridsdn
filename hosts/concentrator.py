#!/usr/bin/python
import socket,sys,traceback
import time, threading
import json
import sys, signal
from array import array


class Aggregator:
    runFlag = True
    s = socket.socket()
    def __init__(self):
        """ Constructor """
        self.bucket = []
        self.listnerThread = threading.Thread(target=self.listen, args=())
        self.bucketWatcherThread = threading.Thread(target=self.bucketWatcher, args=())
        self.listnerThread.start()
        self.bucketWatcherThread.start()

    def listen(self):
        """ concentrator daemon that listens to connections """
        # s = socket.socket()
        host = socket.gethostname()
        try:
            self.s.bind((host,PORT))
            self.s.listen(5)
        except socket.error:
            print "something bad happened:"
            traceback.print_exc()
            sys.exit(1)
        while self.runFlag == True:
            print 'Listening on port %d' % PORT
            c, addr = self.s.accept()
            tempBuffer = c.recv(1024)
            print 'Got connection from ',addr
            print tempBuffer
            if self.runFlag == False:
                continue
            try:
                tempBuffer = json.loads(tempBuffer)
            except ValueError, e:
                print "Error in decoding json" ,  e
                continue
            # Acquire Lock here
            bucketLock.acquire()
            self.bucket.append(tempBuffer)
            bucketLock.release()
            # Release Lock here
            # print type(tempBuffer)
            c.send("ACK")
            c.close()
        return

    def bucketWatcher(self):
        """Check status of bucket"""
        bucketLock.acquire()
        # print "Hello from  bucketWatcher"
        if len (self.bucket) >= 2:
            tempBuffer = self.bucket
            self.bucket = []
            bucketLock.release()
            self.sendUpstream(tempBuffer)
        else:
            bucketLock.release()
        time.sleep(1)
        # print "bye"
        if self.runFlag == True:
            self.bucketWatcher()

    def sendUpstream(self,bufferedData):
        """ Send reading over the network. """

        serialzedReading = json.dumps(bufferedData)

        print "To be sent: %s " % serialzedReading
        # try:
        #     # send reading over TCP socket
        #     s = socket.socket()
        #     host = socket.gethostname()
        #     s.connect((host, PORT))
        #     s.send(serialzedReading)
        #     ack = s.recv(BUFFER_SIZE)
        #     s.close()
        #     print "Received:", ack
        #     return ack
        # except socket.error as errmsg:
        #     print "Socket error: %s" % errmsg

    def stopListening(self):
        """ Stop listner thread """
        # print "killing listener"
        self.runFlag = False
        socket.socket(socket.AF_INET,socket.SOCK_STREAM).connect( ( socket.gethostname() , PORT))
        # self.s.close()
        self.listnerThread.join()


def signalHandler(signal,frame):
    # print "ctrl-c pressed"
    ag.stopListening()
    sys.exit(0)

if __name__=='__main__':
    if len(sys.argv) >= 2:
        PORT = int(sys.argv[1])
    else:
        PORT = 8080
    bucketLock = threading.Lock()
    ag = Aggregator()
    signal.signal(signal.SIGINT,signalHandler)
    signal.pause()
