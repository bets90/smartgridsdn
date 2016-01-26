#!/usr/bin/python
import socket,sys,traceback
PORT = 8080
def mainServer():
    "concentrator daemon that listens to connections"
    s = socket.socket()
    host = socket.gethostname()
    try:
        s.bind((host,PORT))
        s.listen(5)
    except socket.error:
        print "something bad happened:"
        traceback.print_exc()
        sys.exit(1)
    print 'Listening on port %d' % PORT
    while True:
        c, addr = s.accept()
        print 'Got connection from ',addr
        print c.recv(1024)
        #print "Received: ",data
        c.send("ACK")
        c.close()
if __name__=='__main__':
    mainServer()
