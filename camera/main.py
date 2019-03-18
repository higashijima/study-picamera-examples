from flask import Flask, render_template, Response
# from processor.simple_streamer import SimpleStreamer as VideoCamera
# from processor.pedestrian_detector import PedestrianDetector as VideoCamera
# from processor.motion_detector import MotionDetector as VideoCamera
from processor.qr_detector import QRDetector as VideoCamera
# from processor.face_detector import FaceDetector as VideoCamera
# from processor.person_detector import PersonDetector as VideoCamera
import RPi.GPIO as GPIO
import processor.mcp3208 as ADconv

import time
import threading

GPIO.setmode(GPIO.BCM)
# DutyCycle as open
DUTY_OPEN = 2.5
# DutyCycle as close
DUTY_CLOSE = 7.25
# Motor output pin
SERVO_OUT = 12
GPIO.setup(SERVO_OUT, GPIO.OUT)
SERVO = GPIO.PWM(SERVO_OUT, 50)
current_state = DUTY_CLOSE

video_camera = VideoCamera(flip=False)
adc = ADconv.mcp3208(11, 10, 9, 8)

app = Flask(__name__)

def qr_detect():
    detected, data = video_camera.get_detected()
    if detected:
        if not(data == ""):
            current_state = DUTY_OPEN if current_state==DUTY_CLOSE else DUTY_OPEN
            SERVO.CHangeDutyCycle(current_state)
            
@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    qr = False
    value = [0, 0]

    while True:
        value[0] = adc.adc(0)
        value[1] = adc.adc(1)

        print("[{}, {}]".format(value[0], value[1]))
        qr = value[0] < 3400
        qr_detected, ret = video_camera.get_detected()
            
        if qr and qr_detected:
            SERVO.ChangeDutyCycle(DUTY_OPEN)

        if qr:
            SERVO.ChangeDutyCycle(DUTY_CLOSE)

        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(video_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, threaded=True)
