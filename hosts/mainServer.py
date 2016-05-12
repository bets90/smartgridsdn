#!/usr/bin/python

import sqlite3
import json
import socket
import sys
import threading
import traceback
import signal

PORT = 3128
HOST = socket.gethostname()
# Number of records to keep in memory before flushing to database
MAIN_SERVER_CAP = 5

class CollectReading(threading.Thread):
    """Collect Reading from concentrators"""
    s = socket.socket()
    runFlag = True
    readings = []

    def __init__(self):
        super(CollectReading, self).__init__()
        self.listenerThread = threading.Thread(target=self.listen)
        # self.dataThread = threading.Thread(target=self.update_db)
        self.dataSignal = threading.Event()
        self.listenSignal = threading.Event()
        self.reader_lock = threading.Lock()

        self.conn = sqlite3.connect("/tmp/readings.db", check_same_thread=False)
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS readings
            (id, kwh, lastread, PRIMARY KEY (id, lastread))''')
        self.conn.commit()
        self.listenerThread.start()

    def listen(self):
        """Listen to concentrators on different Area"""
        print "Listen"
        try:
            self.s.bind(("", PORT))
            self.s.listen(10)
            print "Listening on port %d" % PORT
        except socket.error:
            print "exception: "
            traceback.print_exc()
        while self.runFlag:
            c, addr = self.s.accept()
            temp_buffer = c.recv(2048)
            if not self.runFlag:
                continue
            try:
                self.readings.extend(json.loads(temp_buffer))
                if len(self.readings) >= MAIN_SERVER_CAP:
                    self.update_db()
                    self.listenSignal.wait()    # wait for the db update to finish before proceeding
            except ValueError:
                print "Error in decoding json"
                #traceback.print_exc()
            finally:
                if self.readings is not None:
                    self.update_db()
                self.listenSignal.wait()
                self.listenSignal.set()
            c.send("SER_ACK")
            c.close()
        return

    def update_db(self):
        try:
            print "Data received"
            rdstmt = []
            print len(self.readings)
            print self.readings
            for reading in self.readings:
                row = (reading['id'], reading['reading'], reading['ts'])
                rdstmt.append(row)

            self.c.executemany("INSERT INTO readings VALUES (?,?,?)", rdstmt)
            self.conn.commit()
            self.readings = []

        except sqlite3.Error as e:
            #traceback.print_exc()
            print e.message
        finally:
            self.listenSignal.set()
        return True

    def stop_listening(self):
        """ Stop listener thread """
        print "killing listener"
        self.runFlag = False
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((socket.gethostname(), PORT))
        self.conn.close()
        self.listenerThread.join()

    def show_data(self, meter_id):
        """Show Data per meterID"""
        cur = self.c.execute("SELECT * FROM readings WHERE id=? ORDER BY lastread", meter_id)
        for row in cur:
            print row


def signal_handler(signal, frame):

    reader.stop_listening()
    sys.exit(0)


def valid_id(meterid):
    try:
        if 0 < int(meterid) < 255:
            return True
        else:
            return False
    except ValueError:
        return False

if __name__ == "__main__":
    reader = CollectReading()
    choice = ""
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
