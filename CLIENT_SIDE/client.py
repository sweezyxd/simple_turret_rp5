import socket as s
from time import sleep, monotonic
import zlib
from threading import Thread
import numpy as np
import cv2
import pickle

width, height = 640, 480

#TODO:
# 1. FINISH SETTING UP PASSWORD
# 2. MAYBE ENCODE ITv

def applyKey(key, client_socket):
    client_socket.sendKey(key)
    if key == ord("q"):
        return True
    return False


class RP_CLIENT:
    def __init__(self, ip, port, passw, shape, buffer_size):
        self.ip, self.port, self.__password = ip, port, passw
        self.shape = shape 
        self.buffer_size = buffer_size

        # Init Image and Data
        self.Image = None
        self.__tosend = None

        # Connecting to the server
        self.client = s.socket(s.AF_INET, s.SOCK_DGRAM)
        self.client.settimeout(1)
        self.client.sendto(passw.encode(), (self.ip, self.port))
        stream_thread = Thread(target=self.__grabImage)
        data_thread = Thread(target=self.__sendData)
        data_thread.start()
        stream_thread.start()

    def __packetSetup(self, data, packet_n) :
        # Result
        ended, packet = False, b""

        if b"ENDED_FRAME" in data:
            data, ended = data[:data.index(b"ENDED_FRAME")], True

        if b"PACKET_NUMBER_" in data and b"END_PACKET_" in data:
            data = data.split(b"PACKET_NUMBER_")[1].split(b"END_PACKET_")[0]

            if int(data[:2]) - packet_n == 0:
                packet_n = int(data[:2]) + 1
                packet = data[2:]

        return ended, packet_n, packet
    
    def __sendData(self):
        while True:
            if self.__tosend:
                self.client.sendto(b"KEY_SENT: " + self.__tosend.encode(), (self.ip, self.port))
                self.__tosend = None
            else:
                self.client.sendto(b"KEY_SENT: None", (self.ip, self.port))
            
                

    def __grabImage(self):
        while True:
            frame, packet_number = b"", 1
            while True:
                try:
                    ended, packet_number, packet = self.__packetSetup(self.client.recvfrom(self.buffer_size)[0], packet_number)
                    frame += packet
                    if ended:
                        break
                    
                except s.timeout:
                    print("Connection Timed Out.")
                    break
            try:
                self.Image = np.frombuffer(frame, dtype=np.uint8).reshape(self.shape)
            except Exception as e:
                print(e)
                pass
                
                
    def sendKey(self, key):
        if not self.__tosend:
            self.__tosend = key



client = RP_CLIENT("192.168.192.168", 5050, "1234", (height, width, 3), 65500)

cv2.namedWindow("stream")

while True:
    if client.Image is not None:
        frame = cv2.warpAffine(client.Image, cv2.getRotationMatrix2D((width // 2, height // 2), 180, 1), (width, height))
        cv2.imshow("stream", frame)
    else:
        cv2.imshow("stream", np.ones(shape=(height, width, 3)) * 0)

    key_pressed = cv2.waitKey(1) & 0xFF
    if key_pressed != 255:
        if applyKey(chr(key_pressed), client):
            break
    sleep(0.01)
