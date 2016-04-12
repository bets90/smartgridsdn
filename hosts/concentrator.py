#!/usr/bin/python
import json
import signal
import socket
import sys
import threading
import time
import traceback


class Aggregator:
    runFlag = True
    s = socket.socket()

    def __init__(self):
        """ Constructor """
        self.bucket = []
        self.listenerThread = threading.Thread(target=self.listen, args=())
        self.bucketWatcherThread = threading.Thread(target=self.bucketWatcher, args=())
        self.listenerThread.start()
        self.bucketWatcherThread.start()

    def listen(self):
        """ concentrator daemon that listens to connections """
        # s = socket.socket()
        host = socket.gethostname()
        try:
            self.s.bind((host, PORT))
            self.s.listen(5)
            print 'Listening on port %d' % PORT
        except socket.error:
            print "something bad happened:"
            traceback.print_exc()
            sys.exit(1)
        while self.runFlag:
            c, addr = self.s.accept()
            tempBuffer = c.recv(1024)
            print 'Got connection from ',addr
            print tempBuffer
            if not self.runFlag:
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
        acquired = bucketLock.acquire()
        try:
            if len(self.bucket) >= 2:
                tempBuffer = self.bucket
                self.bucket = []
                bucketLock.release()
                self.sendUpstream(tempBuffer)
            else:
                bucketLock.release()
            time.sleep(1)
            # print "bye"
            if self.runFlag:
                self.bucketWatcher()
        except thread.error:
            bucketLock.release()
            traceback.print_exc()

        #finally:
        # TODO: check how to unlock here
            #print acquired
            # if acquired:
            #    bucketLock.release()

    def sendUpstream(self, bufferedData):
        """ Send reading over the network. """

        serialzedReading = json.dumps(bufferedData)

        print "To be sent: %s " % serialzedReading
        try:
            # send reading over TCP socket
            s = socket.socket()
            host = socket.gethostname()
            s.connect((host, SERVER_PORT))
            s.send(serialzedReading)
            ack = s.recv(BUFFER_SIZE)
            s.close()
            print "Received:", ack
            return ack
        except socket.error as errmsg:
            print "Socket error: %s" % errmsg

    def stopListening(self):
        """ Stop listner thread """
        # print "killing listener"
        self.runFlag = False
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect( ( socket.gethostname() , PORT))
        # self.s.close()
        self.listenerThread.join()


def signalHandler(signal,frame):
    # print "ctrl-c pressed"
    ag.stopListening()
    sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        PORT = int(sys.argv[1])
        SERVER_PORT = int(sys.argv[2])
    else:
        PORT = 8080
        SERVER_PORT = 3128
    BUFFER_SIZE = 1024
    bucketLock = threading.Lock()
    ag = Aggregator()
    signal.signal(signal.SIGINT, signalHandler)
    signal.pause()
