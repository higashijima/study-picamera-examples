from __future__ import print_function
from flask import Flask, Response
#from pyzbar import pyzbar
#from picamera.array import PiRGBArray
#from picamera import PiCamera
#from datetime import datetime
#import numpy as np
#import cv2

import RPi.GPIO as GPIO
import time

#class QRreader:
#  camera = PiCamera()
#
#  def __init__(self):
#    camera.capture(rawCapture, format="bgr", use_video_port=True)
#    self.frame = rawCapture.array
#    decode_objes(self.frame)
#    draw_position(self.frame, decoded_objs)
#    ret, jpeg = cv2.imencode('.jpg', frame)
#    rawCapture.truncatate(0)


CS_IN = GPIO.LOW
CS_OUT = GPIO.HIGH
CLK_IN = GPIO.LOW
CLK_OUT = GPIO.HIGH

class MCP3208:
  def __init__(self, clk, mosi, miso, cs):
    self.clk = clk
    self.mosi = mosi
    self.miso = miso
    self.cs = cs
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(clk, GPIO.OUT)
    GPIO.setup(mosi, GPIO.OUT)
    GPIO.setup(miso, GPIO.IN)
    GPIO.setup(cs, GPIO.OUT)

  def adc(self, ch):
    if (ch>7 or ch<0):
      return -1

    # channel setting
    channel = ch
    channel |= 0x18
    channel <<= 3

    GPIO.output(self.cs, CS_OUT)  # CS in
    GPIO.output(self.clk, CLK_IN)  # CLK SGL/DIFF
    GPIO.output(self.cs, CS_IN)  # CS in

    for i in range(5):
      if channel & 0x80:
        GPIO.output(self.mosi, GPIO.HIGH)
      else:
        GPIO.output(self.mosi, GPIO.LOW)
      channel <<= 1

      GPIO.output(self.clk, CLK_OUT) # CLK out
      GPIO.output(self.clk, CLK_IN) # CLK in

    value = 0
    for i in range(13):
      GPIO.output(self.clk, CLK_OUT)
      GPIO.output(self.clk, CLK_IN)
      value <<= 1
      if i>0 and GPIO.input(self.miso)==GPIO.LOW:
        value |= 0x1
    GPIO.output(self.cs, CS_OUT)

    return value

RELAY_CTL = 12

def main():
  ADC = MCP3208(11, 10, 9, 8)
#  QR = QRreader()

  GPIO.setup(RELAY_CTL, GPIO.OUT)
  while True:
    for ch in range(2):
      value0= ADC.adc(0)
      value1= ADC.adc(1)
      if value0 < 2048:
        GPIO.output(RELAY_CTL, GPIO.HIGH)

      if value1 < 2048:
        GPIO.output(RELAY_CTL, GPIO.LOW)
      print("{}:{}".format(value0, value1))

if __name__ == '__main__':
  main()

