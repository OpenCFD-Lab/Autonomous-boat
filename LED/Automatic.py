import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
relay_pins = [2, 3, 4]
GPIO.setup(relay_pins, GPIO.OUT, initial=GPIO.HIGH)

try:
    while True:
        GPIO.output(relay_pins[1], GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(relay_pins[1], GPIO.HIGH)
        time.sleep(0.5)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()  # GPIO 핀 초기화
