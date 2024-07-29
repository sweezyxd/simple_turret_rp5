import socket as s
from threading import Thread
import numpy as np
import time
import zlib
import pickle

# TODO:
# 1. ERROR HANDLING
# 2. PROPER PRIVATE/PUBLIC NAMING



def test_func(key):
    print(key)

def array_to_lenghts(data, dividor):
    arr = np.array([])
    divisions = len(data) // dividor

    for n in range(divisions):
        arr = np.append(arr, int(dividor))
    return np.append(arr, round(dividor * ((len(data) / dividor) - (len(data) // dividor))))


class SERVER:
    def __init__(self, ip, port, password, image_shape, buffer_size, recvFunction):
        self.ip, self.port, self.__password, self.image_shape, self.buffer_size = ip, port, password, image_shape, buffer_size
        self.recvFunction = recvFunction
        self.client_address_port, self.sendFlag = None, True #client_address_port is an ip, port tuple, sendFlag is a bool
        self.on = False

        # Starting Connection
        self.server = s.socket(s.AF_INET, s.SOCK_DGRAM)
        self.server.bind((self.ip, self.port))
        self.server.settimeout(5)

        self.__stream_thread = Thread(target=self.__sendImageThread)
        self.__recv_thread = Thread(target=self.__recvDataThread)
        self.__restart_checker_thread = Thread(target=self.__restartChecker)
        
        self.__frame = None

    def __send(self, data):
        try:
            self.server.sendto(data, self.client_address_port)
        except TypeError:
            self.__connectionResetHandler()

    def __recv(self, buffer):
        try:
            return self.server.recv(buffer)
        except TimeoutError:
            self.__connectionResetHandler()
    
    def __recvDataThread(self):
        while self.on:
            data = self.__recv(1024)
            if data is not None and b"KEY_BIND: " in data and data.split(b"KEY_BIND: ")[1] != b"None":
                self.recvFunction(data.decode().split("KEY_SENT: ")[1][:1])
            else:
                self.recvFunction("None")

    def __sendImageThread(self):
        ping = time.monotonic()
        while self.on:
            if self.__frame is not None:
                ping = time.monotonic() - ping
                frame = self.__frame.tobytes()
                buffer_array = np.array(array_to_lenghts(frame, self.buffer_size), dtype=np.int32)
                x, y = 0, "1"
                for n in buffer_array:
                    y = "0" * (2 - len(y)) + y
                    self.__send( "PACKET_NUMBER_{}".format(y).encode()+ frame[x: x + n] + b"END_PACKET_")
                    
                    x += n
                    y = str(int(y) + 1)
                self.__send(b"ENDED_FRAME")
                # Reseting values

                ping = time.monotonic()
                self.sendFlag = False
                self.__frame = None

    def __connectionResetHandler(self):
        self.on = False
        self.server.close()
        self.__init__(self.ip, self.port, self.__password, self.image_shape, self.buffer_size, self.recvFunction)
    
    def __restartChecker(self):
        while True:
            if self.client_address_port is None:
                self.start()
                break
            else:
                time.sleep(1)
    
    def start(self):
        if self.client_address_port is None:
            while True:
                try: 
                    print("listening...")
                    data, self.client_address_port = self.server.recvfrom(1024)
                    print(f"received connection from {self.client_address_port}")
                    break
                except TimeoutError:
                    print("Connection timed out, reseting socket...")
                    #time.sleep(1)
                    #

            time.sleep(1)
            self.sendFlag = True
            self.on = True

            # Starting Threads
            self.__restart_checker_thread.start() 
            self.__stream_thread.start()
            self.__recv_thread.start()
            print("done")
        else:
            print("server already started bro chill")
        

            

    def setFrame(self, frame):
        if self.__frame is None:
            self.__frame = frame

# self, ip, port, password, image_shape, buffer_size, recvFunction

