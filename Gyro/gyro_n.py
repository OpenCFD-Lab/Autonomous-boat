import socket
import requests
from pynmeagps import NMEAReader
import time

######### n ###########
def PostGyroData(gyroAngle):
    UNAME = 'Gyro'
    URL = 'http://192.168.2.12:9014/Gyro'
    with open ("/home/pi/00_ThrusterCode/data/gyroData.dat", 'wt') as gyroFile:
        gyroFile.write(str(gyroAngle)+"\t"+str("EOF"))
    GyroFile_req=open('/home/pi/00_ThrusterCode/data/gyroData.dat', 'rb')
    GyroFile={'GyroFile':GyroFile_req}
    reqData={'uname':UNAME,'fileName':GyroFile}
    try:
        res = requests.post(URL, files=GyroFile, data=reqData, timeout=0.1)
        GyroFile_req.close()
    except requests.exceptions.Timeout:
        PostGyroData(gyroAngle)
########################

UDP_IP="192.168.2.13"
UDP_PORT=5555
dataList=[]

########## filename #############
#datagyro = "/home/pi/00_ThrusterCode/data/j_gyro_r.txt"
#################################

sock=socket.socket (socket.AF_INET,socket.SOCK_DGRAM)
sock.setsockopt (socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
sock.setsockopt (socket.SOL_SOCKET,socket.SO_BROADCAST,1)
sock.bind ((UDP_IP,UDP_PORT))
dateList=[]

data, addr = sock.recvfrom(8192)
dataString = data.decode('utf-8')
data1 = dataString.split(',')

################# dt ##################
totaldt = 0
start_time = time.time()
#####################################

zero = 167

while True:
    ################# dt ##################
    end_time = time.time()
    dt = end_time - start_time
    start_time = end_time
    if dt > 1:
        dt = 0
    totaldt = dt + totaldt
    #####################################

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
        #print(dt)
        #break
        ######### n ###########
        PostGyroData(gyroAngle)
        ########################

 #       with open (datagyro, "w") as f:
 #           f.write(str(gyroAngle) + "\t" + "EOF")

