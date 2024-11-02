import socket
from pynmeagps import NMEAReader
UDP_IP="192.168.2.20"
UDP_PORT=5555
dataList=[]

########## filename #############
datagyro = "/home/pi/00_ThrusterCode/data/j_gyro_r.txt"
#################################

sock=socket.socket (socket.AF_INET,socket.SOCK_DGRAM)
sock.setsockopt (socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
sock.setsockopt (socket.SOL_SOCKET,socket.SO_BROADCAST,1)
sock.bind ((UDP_IP,UDP_PORT))
dateList=[]

data, addr = sock.recvfrom(8192)
dataString = data.decode('utf-8')
data1 = dataString.split(',')

'''
if len(data1)>16:
    zero1 = float(data1[14])
    if float(zero1) > 180:
        zero = float(zero1) - 360
    elif float(zero1) < -180:
        zero = float(zero1) + 360
    zero = zero1 #x축으로 배가 바라볼때 각도
'''
zero = 72

while True:
    data,addr=sock.recvfrom(8192)
    dataString=data.decode('utf-8')
    data1=dataString.split(',')
    
    if len(data1)>16:
        gyroAngle = float(data1[14]) - zero

        if float(gyroAngle) > 180 or float(gyroAngle) < -360:
            gyroAngle = float(gyroAngle) - 360
        elif float(gyroAngle) < -180:
            gyroAngle = float(gyroAngle) + 360

        print(gyroAngle)
    
        with open (datagyro, "w") as f:
            f.write(str(gyroAngle) + "\t" + "EOF")

