#!/usr/bin/env python
#-*- encoding: utf8 -*-

'''
ETRI Social Behavior Recognition ROS Adaptor Node

Author: Minsu Jang (minsu@etri.re.kr)
'''

import socket
import time
import json
import sys
from Queue import Queue
from Queue import Empty
from threading import Thread
from threading import Lock

import cv2
import numpy as np

import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge, CvBridgeError


class ImageTransmitter(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.img_queue = Queue(10)

        self.client_socket = None
        self.addr = 'abc'

        self.connected_ = False
        self.connected_lock = Lock()
        self.exit_ = False
        self.exit_lock = Lock()

        self.pub_recog = rospy.Publisher('recognitionResult', String, queue_size=1)
        rospy.Subscriber('Color_Image', Image, callback=self.image_cb)

    def image_cb(self, msg):
        try:
            bridge = CvBridge()
            frame = bridge.imgmsg_to_cv2(msg, "bgr8")
            self.img_cb(frame)

            cv2.imshow('image', frame)

            cv2.waitKey(1)
        except CvBridgeError as e:
            rospy.logerr(e)

    def connected(self, client_socket, addr):
        self.client_socket = client_socket
        self.addr = addr
        with self.connected_lock:
            self.connected_ = True

    def stop(self):
        with self.exit_lock:
            self.exit_ = True

    # 통신 쓰레드
    def run(self):
        while True:
            time.sleep(0.01)
            #print('again~~~')

            with self.exit_lock:
                if self.exit_ is True:
                    print('exiting...')
                    break

            with self.connected_lock:
                if self.connected_ is False:
                    #print('not connected...')
                    continue

            try:
                data = self.client_socket.recv(1024)

                if not data:
                    print('Disconnected by ' + self.addr[0], ':', self.addr[1])
                    break
                else:
                    result = data.decode()
                    print('DATA: ' + result)
                    if len(result) > 1 and 'call' != result:
                        self.publish_results(result)
            except:
                rospy.logerr('Exception@run')
                break


    def img_cb(self, frame):
        try:
            with self.connected_lock:
                if self.connected_ is False:
                    #print('not connected...')
                    return

            # opencv jpeg encoding / quality 100
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 100]
            _, imgencode = cv2.imencode('.jpg', frame, encode_param)

            data = np.array(imgencode)
            stringData = data.tostring()

            self.client_socket.send(str(len(stringData)).ljust(16).encode())
            self.client_socket.send(stringData)
        except:
            rospy.logerr("Exception@img_cb")
            pass


    def publish_results(self, result_json):
        rospy.logdebug('[%s] publishing: %s', rospy.get_name(), result_json)
        self.pub_recog.publish(result_json)


if __name__ == '__main__':
    rospy.init_node('etri_client_node', anonymous=False)

    rospy.loginfo('[%s] Initializing...', rospy.get_name())

    img_transmitter = ImageTransmitter()
    img_transmitter.start()

    #img_provider = ImageProvider(img_transmitter)
    #img_provider.start()


    # IP address & Port
    HOST = '127.0.0.1'
    PORT = 9999

    # socket 통신 연결
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)

    print('server started. waiting for a client...')
    client_socket, addr = server_socket.accept()
    print('connected')
    # 통신 시작
    img_transmitter.connected(client_socket, addr)
    print('transmit started...')

    rospy.loginfo("[%s] initialized.", rospy.get_name())

    rospy.spin()

    img_transmitter.stop()
    print('stopped')
    img_transmitter.join()
    print('joined')
