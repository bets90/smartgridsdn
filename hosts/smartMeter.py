#!/usr/bin/python           # This is client.py file

import socket,time,random

PORT = 8080
BUFFER_SIZE = 1024

class Reading:
    'Reading object with all the necessary data'
    currentReading = 0.0
    lastReadingTime = time.time()
    def __init__(self):
        self.currentReading = 0;
        self.lastReadingTime = time.time()
    def getLatestReading():
        print self.lastReasingTime + ":" + self.currentReading
        return self.lastReadingTime + ":" + self.currentReading
    def setlastReading(value,timeStamp):
        self.currentReading = value

def generateReading():
    currentTime = time.time()
    time.sleep(10)
    interval = currentTime - Reading.lastReadingTime
    print "Interval is: ", interval
    print random.uniform(0.0,0.01) * interval
    return interval

def sendReadings():
    s = socket.socket()         # Create a socket object
    host = socket.gethostname() # Get local machine name
    s.connect((host, PORT))
    s.send("test")
    print "Received:", s.recv(BUFFER_SIZE)
    s.close

if __name__=='__main__':
    reading = Reading()
    generateReading()
    sendReadings()
