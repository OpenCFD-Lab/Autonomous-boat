import serial
import time
import pigpio as gpio
import numpy as np
import requests
from datetime import datetime
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
relay_pins = [2, 3, 4]
GPIO.setup(relay_pins, GPIO.OUT, initial=GPIO.HIGH)

# LED 초기화 함수 (모든 LED 끄고 특정 LED만 켜기)
def activate_green_led():
    # 모든 LED 끄기
    GPIO.output(relay_pins[0], GPIO.HIGH)  # 1번 LED 끄기
    GPIO.output(relay_pins[1], GPIO.HIGH)  # 2번 LED 끄기
    GPIO.output(relay_pins[2], GPIO.LOW)


def PostThrusterData(LeftThruster, RightThruster, CenterThruster):
    UNAME = 'Thruster'
    URL = 'http://192.168.2.2:9016/Thruster'
    with open("./data/ThrusterData.dat", "w") as ThrusterFile:
        ThrusterFile.write(f"{LeftThruster} {RightThruster} {CenterThruster}\n")
    ThrusterFile_req = open('./data/ThrusterData.dat', 'rb')
    ThrusterFile = {'ThrusterFile': ThrusterFile_req}
    reqData = {'uname': UNAME, 'fileName': ThrusterFile}
    try:
        res = requests.post(URL, files=ThrusterFile, data=reqData)
        ThrusterFile_req.close()
    except requests.exceptions.Timeout:
        PostThrusterData(LeftThruster, RightThruster, CenterThruster)


def ALL_SetPwmValue(Fmax, Bmax, Diff, FB, LR):
    print("read ALL_SetPwmValue")
    try:
        upperLimit = 350
        FB_ = FB
        LR_ = LR
        FB = (FB - 1500) / 400
        LR = (LR - 1500) / (400 * 2)
        Left_Thruster_Offset = max(FB, 0) * Fmax + min(FB, 0) * Bmax + np.sign(FB + 0.00001) * (
                max(LR, 0) + min(LR, 0)) * Diff
        Right_Thruster_Offset = max(FB, 0) * Fmax + min(FB, 0) * Bmax - np.sign(FB + 0.00001) * (
                max(LR, 0) + min(LR, 0)) * Diff
        Left_Thruster_Corrector = upperLimit - max(Right_Thruster_Offset, upperLimit)
        Right_Thruster_Corrector = upperLimit - max(Left_Thruster_Offset, upperLimit)
        Left_Thruster_Offset = min(Left_Thruster_Offset, upperLimit)
        Right_Thruster_Offset = min(Right_Thruster_Offset, upperLimit)
        Left_Thruster = int(1500 + Left_Thruster_Offset + Left_Thruster_Corrector)
        Right_Thruster = int(1500 + Right_Thruster_Offset + Right_Thruster_Corrector)
    except:
        FB_, LR_ = 1500, 1500
        Left_Thruster = 1500
        Right_Thruster = 1500
        print("Error in ALL_SetPwmValue")
    return Left_Thruster, Right_Thruster


def ThrusterOperation(Left_Thruster, Right_Thruster, Center_Thruster):
    try:
        print(f"Left : {Left_Thruster}, Right : {Right_Thruster}")
        print('####################################################')
        pi_connect.set_servo_pulsewidth(19, Left_Thruster)
        pi_connect.set_servo_pulsewidth(20, Right_Thruster)
        activate_green_led()
    except KeyboardInterrupt:
        print("Error: KeyboardInterrupt")
        pi_connect.set_servo_pulsewidth(19, 1500)
        pi_connect.set_servo_pulsewidth(20, 1500)
    except:
        print("Error: Exception")
        pi_connect.set_servo_pulsewidth(19, 1500)
        pi_connect.set_servo_pulsewidth(20, 1500)


Running = True
criticalError = False

try:
    arduinoPort = "/dev/ttyACM0"
    reception = serial.Serial(arduinoPort, 9600)
    pi_connect = gpio.pi()
except:
    pi_connect.set_servo_pulsewidth(19, 1500)
    pi_connect.set_servo_pulsewidth(20, 1500)
    criticalError = True

if criticalError:
    while True:
        print('CRITICAL ERROR: ARDUINO PORT IS NOT DEFINED')
        pi_connect.set_servo_pulsewidth(19, 1500)
        pi_connect.set_servo_pulsewidth(20, 1500)

#############################################
maxF = 100
maxB = 50
maxR = 100
#############################################

while Running:
    try:
        rawRC = reception.readline().decode('utf-8', errors='ignore').split(" ")
        if len(rawRC) == 3 and rawRC[0] != '' and 1100 <= int(rawRC[0]) <= 1900:
            LR = int(rawRC[0])
            FB = int(rawRC[1])
            CH3 = int(rawRC[2].strip("\n").strip("\r"))
            print('::::RC mode::::')
            print(FB, LR)

            if CH3 > 1700:
                print('Stopping RC control due to channel values.')
                pi_connect.set_servo_pulsewidth(19, 1500)
                pi_connect.set_servo_pulsewidth(20, 1500)
                os.system("sudo shutdown -h now")
                break

            if 1100 <= LR <= 1900:
                LT, RT = ALL_SetPwmValue(maxF, maxB, maxR, FB, LR)
                CT = int((LT + RT) / 2)
                ThrusterOperation(LT, RT, CT)
                print(datetime.now())
                with open('./data/thruster.dat', 'a') as test:
                    test.write(str(datetime.now()) + ' ' + str(LT) + ' ' + str(RT) + '\n')
                # PostThrusterData(LeftThruster,RightThruster,CenterThruster)

    except KeyboardInterrupt:
        LT = RT = CT = FB = LR = 1500
        pi_connect.set_servo_pulsewidth(19, 1500)
        pi_connect.set_servo_pulsewidth(20, 1500)
        Running = False
        break
    except Exception as e:
        print(f"Unexpected error: {e}")
        LT = RT = CT = FB = LR = 1500
        pi_connect.set_servo_pulsewidth(19, 1500)
        pi_connect.set_servo_pulsewidth(20, 1500)
        Running = False
        break

# 프로그램 종료 시 GPIO 핀 해제
GPIO.cleanup()
