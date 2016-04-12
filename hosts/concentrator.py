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
        self.bucketWatcherThread = threading.Thread(target=self.bucket_watcher, args=())
        self.listenerThread.start()
        self.bucketWatcherThread.start()

    def listen(self):
        """ concentrator daemon that listens to connections """
        # s = socket.socket()
        host = socket.gethostname()
        try:
            self.s.bind(("", PORT))
            self.s.listen(5)
            print 'Listening on port %d' % PORT
        except socket.error:
            print "something bad happened:"
            traceback.print_exc()
            sys.exit(1)
        while self.runFlag:
            c, addr = self.s.accept()
            temp_buffer = c.recv(1024)
            print 'Got connection from ', addr
            print temp_buffer
            if not self.runFlag:
                continue
            try:
                temp_buffer = json.loads(temp_buffer)
            except ValueError, e:
                print "Error in decoding json", e
                continue
            # Acquire Lock here
            bucketLock.acquire()
            self.bucket.append(temp_buffer)
            bucketLock.release()
            # Release Lock here
            # print type(temp_buffer)
            c.send("ACK")
            c.close()
        return

    def bucket_watcher(self):
        """Check status of bucket"""
        acquired = bucketLock.acquire()
        try:
            if len(self.bucket) >= 2:
                temp_buffer = self.bucket
                self.bucket = []
                bucketLock.release()
                self.send_upstream(temp_buffer)
            else:
                bucketLock.release()
            time.sleep(1)
            # print "bye"
            if self.runFlag:
                self.bucket_watcher()
        except threading.ThreadError:
            bucketLock.release()
            traceback.print_exc()

    def send_upstream(self, buffered_data):
        """ Send reading over the network. """

        serialized_buffer_data = json.dumps(buffered_data)

        print "To be sent: %s " % serialized_buffer_data
        try:
            # send reading over TCP socket
            s = socket.socket()
            host = socket.gethostname()
            s.connect((host, SERVER_PORT))
            s.send(serialized_buffer_data)
            ack = s.recv(BUFFER_SIZE)
            s.close()
            print "Received:", ack
            return ack
        except socket.error as err_msg:
            print "Utility server (%s) is not responding. Data not sent." % host
            print "Network error: %s" % err_msg

    def stop_listening(self):
        """ Stop listener thread """
        # print "killing listener"
        self.runFlag = False
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect( ( socket.gethostname() , PORT))
        # self.s.close()
        self.listenerThread.join()


def signal_handler(signal, frame):
    # print "ctrl-c pressed"
    ag.stop_listening()
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
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
