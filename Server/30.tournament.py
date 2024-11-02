####################  import  #########################
import serial
import math
import time
#import pigpio as gpio
import numpy as np
import os
import requests
from datetime import datetime

############ n ##############
def PostThrusterData(leftThruster, rightThruster):
    UNAME = 'Thruster'
    URL = 'http://192.168.2.9:9026/Thruster'
    with open("/home/opencfd/mins/Thruster/ThrusterData.dat","w") as ThrusterFile:
        ThrusterFile.write(str(int(leftThruster)) + '\t' + str(int(rightThruster)) + '\t' + str("EOF"))
    ThrusterFile_req = open('/home/opencfd/mins/Thruster/ThrusterData.dat','rb')
    ThrusterFile = {'ThrusterFile':ThrusterFile_req}
    reqData = {'uname':UNAME, 'fileName':ThrusterFile}
    try:
        res = requests.post(URL, files=ThrusterFile, data=reqData)
        ThrusterFile_req.close()
    except requests.exceptions.Timeout:
        PostThrusterData(leftThruster , rightThruster)
########################################

####################  RC  #########################
def ALL_SetPwmValue(Fmax, Bmax, Diff, FB, LR):
    # print("read ALL_SetPwmValue")
    try:
        upperLimit = 350
        FB_ = FB
        LR_ = LR
        FB = (FB - 1500) / (400)
        LR = (LR - 1500) / (400 * 2)
        leftThruster_Offset = max(FB, 0) * Fmax + min(FB, 0) * Bmax + np.sign(FB + 0.00001) * (
                    max(LR, 0) + min(LR, 0)) * Diff
        rightThruster_Offset = max(FB, 0) * Fmax + min(FB, 0) * Bmax - np.sign(FB + 0.00001) * (
                    max(LR, 0) + min(LR, 0)) * Diff
        leftThruster_Corrector = upperLimit - max(rightThruster_Offset, upperLimit)
        rightThruster_Corrector = upperLimit - max(leftThruster_Offset, upperLimit)
        leftThruster_Offset = min(leftThruster_Offset, upperLimit)
        rightThruster_Offset = min(rightThruster_Offset, upperLimit)
        leftThruster = int(1500 + leftThruster_Offset + leftThruster_Corrector)
        rightThruster = int(1500 + rightThruster_Offset + rightThruster_Corrector)
        centerThruster = min(Fmax,FB_)
        print(leftThruster, " , ", rightThruster)
    except:
        FB_, LR_ = 1500, 1500
        leftThruster = 1500
        rightThruster = 1500
        # print("read out ALL_SetPwmValue")
    return leftThruster, rightThruster


####################  Thruster  #########################
def ThrusterOperation(leftThruster, rightThruster, centerThruster):  # pwm으로 pin번호 지정, 전달
    #leftThruster =1500
    #rightThruster =1500
    try:
        leftThruster = 1500
        rightThruster = 1500
        #########################################################
        PostThrusterData(leftThruster, rightThruster)
        #########################################################
    except KeyboardInterrupt:
        leftThruster = 1500
        rightThruster = 1500
        #########################################################
        PostThrusterData(leftThruster, rightThruster)
        #########################################################
    except:
        leftThruster = 1500
        rightThruster = 1500
        #########################################################
        PostThrusterData(leftThruster, rightThruster)
        #########################################################


#################### filename ####################
gpsFile = "/home/opencfd/mins/GPS/gpsData.dat"
gyroFile = "/home/opencfd/mins/Gyro/gyroData.dat"
lidarFile = "/home/opencfd/mins/Lidar/lidarData.dat"
cameraFile = "/home/opencfd/mins/Camera/cameraData.dat"
serverFile = "/home/opencfd/mins/Thruster/09029.txt"

count_for_finalTarget = 0
#count_for_C = 1
#countFile_for_C = 4

camera_in_target = 100
angle_from_camera = 360

arriveRange = 1
targetRange = 1.8
inplace = 30

#################### 초기 gps ####################
with open(gpsFile, "r") as gps:
    gps = gps.readline().split("\t")
    nowX = float(gps[0])
    nowY = float(gps[1])

# 목표 위치 설정
finalTargetX = [2.5 , 2.5]#[3   , 4.7 , 5.3 , 2.6 ] 
finalTargetY = [75, 100]#[12.6, 12.5, 9.3 , 5.4 ] 


targetX = finalTargetX[count_for_finalTarget]
targetY = finalTargetY[count_for_finalTarget]

Xlist = []
Ylist = []
#################### 초기 gyro ####################
with open(gyroFile, "r") as gyroData:
    gyro = gyroData.readline().split("\t")
    headangle = float(gyro[0])

#################### 추진기 세팅 ####################
# 추진기 최대/최소값을 설정합니다.
centerThruster = 1500
maxThruster = 1850  # 최대값
minThruster = 1150  # 최소값

forward_max = 50
rotation_max = 150

firstF = addF = 0
firstR = addR = 0

#################### dt 세팅 ####################
totaldt = 0
start_time = 0

#################### list 세팅 ####################
Xlist = []
Ylist = []
gyrolist = []
obstacle = []

finalX_diff = finalTargetX[count_for_finalTarget] - nowX
finalY_diff = finalTargetY[count_for_finalTarget] - nowY
distance = (finalX_diff ** 2 + finalY_diff ** 2) ** 0.5
angle_to_target = math.degrees(math.atan2(finalX_diff, finalY_diff))

for i in range(202):
    obstacle.append(str("0") + " ")
distance_from_lidar = 0
angle_from_lidar = 0

#################### 파일 세팅 ####################
with open(serverFile, "w") as server:
    server.write("dt\tLT\tRT\tF\tR\ttargetX\ttargetY\tnowX\tnowY\tdisToFinal\tdistance\tangleToFinal\tangle_to_target\tangle_from_camera\tcameraOn\theadangle\tlidardis\tlidarangle\tfinaltargetX\tfinaltargetY\n")

#################### True/False ####################
cameraOn = False
Running = True
gpsUpdate = False
arrivedInplace = False
toTarget = False
CWKIM_arriveTarget = False
CWKIM_rotationMotion = False
CWKIM_stopTime = 5 
CWKIM_rotationTime = 0
CWKIM_dectectingCamera = 0
CWKIM_rotationEquationValue = 5.3
CWKIM_forwardEquationValue = 39
CWKIM_forwardMinimum = 43
CWKIM_rotationMinimum = 40
#CWKIM_forwardRatio = 0.2
#CWKIM_rotationRatio = 1 - CWKIM_forwardRatio

# forwardRatio  와 rotationRatio의 값의 합은 무조건 1이어야함


while Running:
    #################### RC ####################
    try:

        if count_for_finalTarget == 0:  # 장애물 인식 1임무
            CWKIM_rotationEquationValue = 7.5 #5.3
            CWKIM_forwardEquationValue = 125 #39 
            CWKIM_forwardMinimum = 43
            CWKIM_rotationMinimum = 40
            targetRange = 2.5
            arrivedRange = 1
            forward_max = 200 
            rotation_max = 380
        elif count_for_finalTarget == 1:
            CWKIM_rotationEquationValue = 5.3
            CWKIM_forwardEquationValue = 30
            CWKIM_forwardMinimum = 30
            CWKIM_rotationMinimum = 40
            targetRange = 1.8
            arrivedRange = 1
            forward_max = 50
            rotation_max = 150
        elif count_for_finalTarget == 2:  # 그림 인식
            CWKIM_rotationEquationValue = 5.3
            CWKIM_forwardEquationValue = 55
            CWKIM_forwardMinimum = 30
            CWKIM_rotationMinimum = 40
            targetRange = 2.5
            arrivedRange = 1
            forward_max = 150
            rotation_max = 300
        elif count_for_finalTarget == 3:  # 장애물 인식 3임무  (1)
            CWKIM_rotationEquationValue = 5.3
            CWKIM_forwardEquationValue = 35
            CWKIM_forwardMinimum = 30
            CWKIM_rotationMinimum = 40
            targetRange = 1.8
            arrivedRange = 1
            forward_max = 50
            rotation_max = 150
        elif count_for_finalTarget == 3:  # 장애물 인식 3임무  (2)
            CWKIM_rotationEquationValue = 5.3
            CWKIM_forwardEquationValue = 35
            CWKIM_forwardMinimum = 30
            CWKIM_rotationMinimum = 40
            targetRange = 1.8
            arrivedRange = 1
            forward_max = 50
            rotation_max = 150
        else:  # 만약을 대비한 코드
            CWKIM_rotationEquationValue = 5.3
            CWKIM_forwardEquationValue = 35
            CWKIM_forwardMinimum = 30
            CWKIM_rotationMinimum = 40
            targetRange = 1.8
            arrivedRange = 1
            forward_max = 50
            rotation_max = 150

        # dt
        end_time = time.time()
        dt = end_time - start_time
        start_time = end_time
        if dt > 1:
            dt = 0
        totaldt = dt + totaldt

        # 현재 위치와 목표 위치 간의 거리 계산
        finalX_diff = finalTargetX[count_for_finalTarget] - nowX
        finalY_diff = finalTargetY[count_for_finalTarget] - nowY
        distance_to_finalTarget = (finalX_diff ** 2 + finalY_diff ** 2) ** 0.5
        angle_to_finalTarget = math.degrees(math.atan2(finalX_diff, finalY_diff))

        if 0 < headangle <= 180:
            if - 180 < angle_to_finalTarget < (headangle - 180):
                angle_to_finalTarget = 360 - (headangle - angle_to_finalTarget)
            else:
                angle_to_finalTarget = angle_to_finalTarget - headangle
        elif -180 <= headangle < 0:
            if (180 + headangle) < angle_to_finalTarget <= 180:
                angle_to_finalTarget = (angle_to_finalTarget - headangle) - 360
            else:
                angle_to_finalTarget = angle_to_finalTarget - headangle
        else:
            angle_to_finalTarget = angle_to_finalTarget - headangle

        if angle_to_finalTarget < -90 or 90 < angle_to_finalTarget:
            distance_to_finalTarget = -distance_to_finalTarget


        # 목표에 도달했는지 확인
        if abs(distance_to_finalTarget) < arriveRange:  # 목표에 가까워지면 종료
            print("####################################################################### 도착1")
            arrivedInplace = True
            toTarget = False

            leftThruster = 1500
            rightThruster = 1500
            #########################################################
            PostThrusterData(leftThruster, rightThruster)
            #########################################################
            #time.sleep(3) # modified by CWKIM
            CWKIM_arriveTarget = True


            #Running = False0
            #break

            if count_for_finalTarget == len(finalTargetX) - 1:
                leftThruster = 1500
                rightThruster = 1500
                #########################################################
                PostThrusterData(leftThruster, rightThruster)
                #########################################################
                print("####################################################################### 도착2")
                break  # 루프를 종료합니다.




            count_for_finalTarget += 1

            #print("modified by CWKIM  : 타겟 도착 후 loop문 다시 처움 부터 시작함")
            #continue  # modified by CWKIM
            
            finalX_diff = finalTargetX[count_for_finalTarget] - nowX
            finalY_diff = finalTargetY[count_for_finalTarget] - nowY
            distance_to_finalTarget = (finalX_diff ** 2 + finalY_diff ** 2) ** 0.5
            angle_to_finalTarget = math.degrees(math.atan2(finalX_diff, finalY_diff))  ## ??

            continue  # modified by CWKIM


        toTarget = False
        #################### lidar ####################
        with open(lidarFile, "r") as lidarData:
            lidar = lidarData.read().split('\n')

            if len(lidar) == 3:
                way = lidar[0].split("\t")
                obstacle = lidar[1]
                obstacle = eval(obstacle)
                obstacle = list(map(float, obstacle))
                EOF_form_lidar = lidar[-1]

                angle_from_lidar = float(way[0])
                distance_from_lidar = float(way[1])

                if EOF_form_lidar == "EOF":
                    if arrivedInplace:
                        print("####################################################################### 제자리회전(장애물 인식 안함)")
                        distance_from_lidar = 0
                        #angle_from_lidar = 0  #Modified by CWKIM
                        angle_from_lidar = angle_to_finalTarget

                        if angle_to_finalTarget < inplace:
                            arrivedInplace = False

                    if abs(distance_to_finalTarget) < targetRange: # or distance_to_finalTarget < 0:
                        toTarget = True

                    #if toTarget:
                    #modified by CWKIM
                    if toTarget or CWKIM_arriveTarget:
                        print("####################################################################### 목적지로 가는 중(장애물 인식 안함)")
                        distance_from_lidar = distance_to_finalTarget
                        #angle_from_lidar = 0
                        angle_from_lidar = angle_to_finalTarget


                    if abs(angle_from_lidar) > 70:
                        print("####################################################################### 길이 없음")
                        targetX = 1500
                        targetY = 1500

                        distance = 0
                        angle_to_target = angle_from_lidar

                    elif distance_from_lidar == 0 and angle_from_lidar == 0:
                        print("####################################################################### 장애물 없음")
                        targetX = finalTargetX[count_for_finalTarget]
                        targetY = finalTargetY[count_for_finalTarget]

                        distance = distance_to_finalTarget
                        angle_to_target = angle_to_finalTarget

                    else:
                        print("####################################################################### 장애물 피하는 중")
                        X_form_lidar = float(distance_from_lidar * math.cos(math.radians(90 - angle_from_lidar)))
                        Y_form_lidar = float(distance_from_lidar * math.sin(math.radians(90 - angle_from_lidar)))

                        if -90 <= headangle <= 90:
                            targetX = nowX + X_form_lidar
                            targetY = nowY + Y_form_lidar
                        else:
                            targetX = nowX - X_form_lidar
                            targetY = nowY - Y_form_lidar

                        angle_to_target = angle_from_lidar
                        distance = distance_from_lidar


        if camera_in_target == count_for_finalTarget:
            print("####################################################################### 그림 보기 위해")
            targetX = finalTargetX[count_for_finalTarget]
            targetY = finalTargetY[count_for_finalTarget]

            angle_to_target = angle_to_finalTarget
            distance = 0

            print(angle_to_finalTarget)
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            if abs(angle_to_finalTarget) <= 20:
                cameraOn = True
                camera_in_target -= 1

        #else:
        #    cameraOn = False

   

        if cameraOn:
            with open (cameraFile,"r") as cameraData:
                camera = cameraData.readline().split("\t")
                EOF_form_camera = camera[-1]

                if EOF_form_camera =="EOF":
                    angle_from_camera = float(camera[0])
                    if angle_from_camera != 360:
                        print("####################################################################### 그림 인식함")
                        X_form_camera = float(distance_from_lidar * math.cos(math.radians(90 - angle_from_camera)))
                        Y_form_camera = float(distance_from_lidar * math.sin(math.radians(90 - angle_from_camera)))

                        if CWKIM_rotationMotion == False: 
                            CWKIM_dectectingCamera = 1


                        if -90 <= headangle <= 90:
                            targetX = nowX + X_form_camera
                            targetY = nowY + Y_form_camera
                        else:
                            targetX = nowX - X_form_camera
                            targetY = nowY - Y_form_camera

                        angle_to_target = angle_from_camera
                        distance = 0


                        if abs(angle_from_camera) < 5 and CWKIM_rotationMotion == False:
                            cameraOn = False

                        '''
                        if abs(angle_from_camera) < 10:
                            cameraOn = False
                            addF = firstF
                            addR = firstR
                        '''
                    else:
                        angle_to_target = angle_from_lidar
                        distance = distance_from_lidar

                        if CWKIM_dectectingCamera == 1:
                            cameraOn = False



        #print("CWKIM_dectectingCamera : ", CWKIM_dectectingCamera)
        #if count_for_finalTarget == camera_in_target +3:
        #    addF = firstF/2
        #    addR = firstR/2

        #if abs(distance_to_finalTarget) < 2 and distance !=0:
        #   addF = firstF/2
        #    addR = firstR/2


        # 거리와 각도에 따라 속도 조절
        # modified by CWKIM
        # start
        forward = abs(distance) * CWKIM_forwardEquationValue #39  # 거리 기반 직진 속도
        rotation = abs(angle_to_target) * CWKIM_rotationEquationValue #5.3 # 각도 기반 회전 속도

        # 전진과 회전값의 비율 조절
        # 회전값이 클수록 전진 값을 낮추는 방식으로 구성
        #CWKIM_rotationRatio = rotation / rotation_max
        #CWKIM_forwardRatio = 1 - CWKIM_rotationRatio

        CWKIM_rotationRatio = 1 - (abs(angle_to_target) / 30) 

        forward = forward * CWKIM_rotationRatio
        #CWKIM_forwardRatio = 1 - CWKIM_rotationRatio
        #forward = CWKIM_forwardRatio * forward
        if forward < CWKIM_forwardMinimum:  # 25
            forward = CWKIM_forwardMinimum

        #print("CWKIM rotationRatio : ", float(CWKIM_rotationRatio), "CWKIM forwardRatio", float(CWKIM_forwardRatio))
        #print("CWKIM >> 1차로 계산된 rotation : ", float(rotation), "1차로 계산된 forward : ", float(forward))

        #목표물까지의 각도 차이가 60도 이상인 경우에는 제자리회전 하는 코드
        if(abs(angle_to_target) > 30):
            #forward = 0
            distance = 0
            #print("angle to target 각도가 60도 이상임// forward : 0, rotation : ", float(rotation))


        # 목표물에 도착했을때 3초동안은 아래에 계산에 따라 움직이도록 설정
        if(CWKIM_arriveTarget == True):
            if(CWKIM_rotationMotion == False):
                CWKIM_rotationTime = time.time() + CWKIM_stopTime
                CWKIM_rotationMotion = True

            print("목표 도착후 제자리 회전 _3초동안 진행될 예정임")
            #print("CWKIM >> 목표 도착후 제자리 회전 _3초동안 진행될 예정임")
            #forward = 0             # 제자리 회전할때는 전진값 0
            distance = 0
            rotation = 80           # 회전값만 고정  # 이건 유동적으로 변경 예정

            if (time.time() > CWKIM_rotationTime) and (abs(angle_to_finalTarget) < 17):
                #print("CWKIM >> 목표 도착후 제자리 회전 종료")
                CWKIM_arriveTarget = False
                CWKIM_rotationMotion = False
                CWKIM_rotationTime = 0


        if abs(rotation) < CWKIM_rotationMinimum: #40
            rotation = CWKIM_rotationMinimum  #40
        #end



        if distance <= 0:
            forward = 0
        else:
            forward = forward + addF


        if angle_to_target == 0:
            rotation = 0
        else:
            rotation = rotation + addR

        if forward > forward_max:
            forward = forward_max
        if rotation > rotation_max:
            rotation = rotation_max

        #print("CWKIM >> 최종적으로 들어가는 rotation : ", float(rotation), "최종적으로 들어가는 forward : ", float(forward))

        rotation = rotation / 2

        # 좌우 추진기 값 계산
        if angle_to_target > 0:
            rightTC = rotation + rotation * 0.05
            leftTC = rotation - rotation * 0.05
            leftThruster = centerThruster + forward + leftTC
            #leftThruster = centerThruster + forward + rotation
            rightThruster = centerThruster + forward - rightTC
            #rightThruster = centerThruster + forward - rotation
        else:
            rightTC = rotation - rotation * 0.05
            leftTC = rotation + rotation * 0.05
            leftThruster = centerThruster + forward - leftTC
            rightThruster = centerThruster + forward + rightTC

        # 추진기 값 제한
        if rightThruster < minThruster:
            rightThruster = minThruster
        if leftThruster < minThruster:
            leftThruster = minThruster

        if rightThruster > maxThruster:
            rightThruster = maxThruster
        if leftThruster > maxThruster:
            leftThruster = maxThruster


        # 결과 출력
        print("=====================================================================")
        print("왼쪽 추진기:", int(leftThruster), "오른쪽 추진기:", int(rightThruster))
        print(f"finaltarget: {finalTargetX[count_for_finalTarget]}, targetY: {finalTargetY[count_for_finalTarget]}")
        #print("target: ",targetX , "targetY: ", targetY)
        print(f"X: {nowX}, Y: {nowY}")
        print("cam: ", angle_from_camera, " ", "camOn: ", cameraOn)
        print(cameraOn, " ", count_for_finalTarget)
        print("dis: ", distance_to_finalTarget)
        #print("angle: ", angle_to_finalTarget)
        #print(forward, " ", rotation)
        #print(angle_to_target)
        
        #print(addF, " ", addR)
        print(" ")

        #########################################################
        PostThrusterData(leftThruster, rightThruster)
        #########################################################

        if totaldt > 0.5:
            totaldt = 0
            with open(serverFile, "a") as server:
                server.write(str(dt) + "\t" + str(leftThruster) + "\t" + str(rightThruster) + "\t"
                             + str(forward) + "\t" + str(rotation) + "\t" + str(targetX) + "\t"
                             + str(targetY) + "\t" + str(nowX) + "\t" + str(nowY) + "\t"
                             + str(distance_to_finalTarget) + "\t" + str(distance) + "\t"
                             + str(angle_to_finalTarget) + "\t" + str(angle_to_target) + "\t"
                             + str(angle_from_camera) + "\t" + str(cameraOn) + "\t"
                             + str(headangle) + "\t" + str(distance_from_lidar) + "\t" + str(angle_from_lidar) + "\t"
                             + str(finalTargetX[count_for_finalTarget]) + "\t"
                             + str(finalTargetY[count_for_finalTarget]) + "\t" + "\n")

        '''
        Cdata = f'/home/pi/mins/Server/C/rev{countFile_for_C}/logData_{count_for_C}.dat'
        count_for_C +=1
        
        with open(Cdata, 'w') as data:
            headangle = 90 - headangle
            angle_to_finalTarget = 90 - angle_to_finalTarget

            if headangle > 180:
                if headangle > 180:
                    headangle -= 360
                if headangle < -180:
                    headangle += 180

            if angle_to_finalTarget > 180:
                if angle_to_finalTarget > 180:
                    angle_to_finalTarget -= 360
                if angle_to_finalTarget < -180:
                    angle_to_finalTarget += 180

            data.write(str(dt) + " " + str(nowX) + " " + str(nowY) + " " + str(targetX) + " " + str(
                targetY) + " " + str(angle_to_finalTarget) + " " + str(distance) + " " + str(headangle) + " " + str(
                gpsUpdate) + " " + str(leftThruster) + " " + str(rightThruster) + " " + str(
                centerThruster) + " " + str(angle_to_finalTarget) + " " + str(finalTargetX[count_for_finalTarget]) + " " + str(
                finalTargetY[count_for_finalTarget]) + "\n")
            for i in range(len(obstacle)):
                data.write(str(obstacle[i]) + " ")
            data.write("\n" + str("[") + str("-100") + str(",") + str("-1") + str("]") + "\n" +
                       str("6524") + "\n" +
                       str("eof"))
            '''
        #################### gyro ####################
        with open(gyroFile, "r") as gyroData:
            gyro = gyroData.readline().split("\t")
            EOF_form_gyro = gyro[-1]

            if EOF_form_gyro == 'EOF':
                headangle = float(gyro[0])

        #################### GPS ####################
        speed = 0.0042 * forward
        d = speed * dt
        with open(gpsFile, "r") as gpsData:
            gps = gpsData.readline().split("\t")
            EOF_form_gps = gps[-1]

            if EOF_form_gps == "EOF":
                print(gps)
                nowX = float(gps[0])
                nowY = float(gps[1])

                
                Xlist.append(nowX)
                Ylist.append(nowY)

                if len(Xlist) > 1 and len(Xlist) > 1:
                    if Xlist[0] != Xlist[1] or Ylist[0] != Ylist:
                        gpsUpdate = True
                        # print("True")
                    else:
                        gpsUpdate = False
                        # print("False")

                if len(Xlist) > 1:
                    if Xlist[0] != Xlist[1]:
                        nowX = float(Xlist[1])
                    #else:
                        #nowX = nowX + d * math.sin(math.radians(float(headangle)))
                    Xlist.pop(0)

                if len(Ylist) > 1:
                    if Ylist[0] != Ylist[1]:
                        nowY = float(Ylist[1])
                    #else:
                        #nowY = nowY + d * math.cos(math.radians(float(headangle)))
                    #Ylist.pop(0)

            #else:
                #nowX = nowX + d * math.sin(math.radians(float(headangle)))
                #nowY = nowY + d * math.cos(math.radians(float(headangle)))

                gpsUpdate = False
                 
    ################################################
    except KeyboardInterrupt:
        leftThruster = 1500
        rightThruster = 1500
        PostThrusterData(leftThruster, rightThruster)
        
        Running = False
        print("KeyboardInterrupt")
        break

    except ValueError:
        leftThruster = 1500
        rightThruster = 1500
        PostThrusterData(leftThruster, rightThruster)
        
        Running = False
        print("ValueError")
        break

    ################################################
