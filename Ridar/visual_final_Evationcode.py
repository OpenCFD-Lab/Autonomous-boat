import math
import matplotlib.pyplot as plt

plt.ion()
fig, ax = plt.subplots()

j = 0

obstacleRange = 3
betweenDistance_range = 0.7
betweenAngle_range = 10
sidePath_angleRange = 30
nearObstacleRange = 2
separateAngleRange = 2
separateDistanceRange = 0.2
checkAngle = 10
checkDistance = 0.3
dangerZoneRange = 1

while True:
    try:
        distance = []
        print("loop start")
        #with open(recent_file, 'r') as h:
        with (open(f"C:/Users/LGUser/Desktop/kaboat/Lidar/case/0510/test1/Lidar_{j}.dat", 'r') as h):
            distance = h.read().split(' ')
            print('j:',j)
            j += 1

            # raw data 읽어오는 부분 #

            #raw data 중 사용할 범위의 거리 distance list에 추가하고 server로 넘겨줄 list에 필요한 data 추가
            distanceList_to_server = []
            distanceList_to_server = distance.copy()
            after_distanceList_to_server = []
            readDistance = []

            if len(distance) == 360:

                # server에 전달하는 raw data 정리하는 부분 #

                # server에서 필요한 범위는 -100˚~100˚ 이므로 필요없는 범위 삭제
                del distanceList_to_server[101:260]
                if len(distanceList_to_server) == 201:
                    #-100˚~100˚ 순서대로 list에 정렬
                    for a in range(100, len(distanceList_to_server)):
                        after_distanceList_to_server.append(distanceList_to_server[a])
                    for a in range(0, 101):
                        after_distanceList_to_server.append(distanceList_to_server[a])

                # lidar 코드에서 사용하는 raw data 정리하는 부분 #

                # lidar 코드에서 사용하는 범위는 -60˚~60˚ 이므로 필요없는 범위 지우고 readDistacne list에 추가
                del distance[60:300]
                readDistance = list(map(float, distance))
                afterDistance = []
                rawAngle = []
                # -60˚~60˚ 순서대로 list에 정렬하고 각도 list를 만들어 거리 list index를 이용해  추가
                for i in range(60,len(distance)):
                    afterDistance.append(readDistance[i])
                    rawAngle.append(i-120)
                for i in range(0,60):
                    afterDistance.append(readDistance[i])
                    rawAngle.append(i)
                # 라이다에서 인식한 거리가 10m 이상일땐, 10m로 변환
                for i in range(0,len(afterDistance)):
                    if float(afterDistance[i]) == 0:
                        #afterDistance[i] = afterDistance[i-1]
                        afterDistance[i] = 10
                    if  float(afterDistance[i]) > 10:
                        afterDistance[i] = 10

                # obstacle 인식하는 부분 #

                obstacleDistance = []
                obstacleAngle = []
                #장애물로 인식하는 범위내에 들어온 물체의 각도 및 거리를 list에 추가
                for k in range(0,len(afterDistance)):
                    if 0 < float(afterDistance[k]) <= float(obstacleRange):
                        obstacleDistance.append(afterDistance[k])
                        obstacleAngle.append(rawAngle[k])
                print('obstacleAngle',obstacleAngle)
                print('obstacleDistance',obstacleDistance)
                print('len(obstacleAngle)',len(obstacleAngle))

                # 경로 계산이 필요하지 않을때, server로 전송하는 정보

                # 장애물이 없을 때, server로 전송하는 정보
                if len(obstacleAngle) == 0 :
                    print('No obstacle')
                    # with open('/home/pi/00_ThrusterCode/data/lidarData.txt','w') as l:
                    #    l.write('0' + '\t' + '0' + '\n' + str(after_distanceList_to_server) +'\n' + 'EOF')
                    # angle_to_server = 0
                    # distance_to_server = 0
                    # PostLidarData(angle_to_server, distance_to_server, after_distanceList_to_server)

                    continue
                # 장애물이 한개 있을때, server로 전송하는 정보
                if len(obstacleAngle) == 1:
                    print('One obstalce')
                    # with open('/home/pi/00_ThrusterCode/data/lidarData.txt','w') as l:
                    #    l.write('0' + '\t' + '0' + '\n' + str(after_distanceList_to_server) +'\n' + 'EOF')
                    # angle_to_server = 0
                    # distance_to_server = 0
                    # PostLidarData(angle_to_server, distance_to_server, after_distanceList_to_server)

                    continue
                stopmove = 0
                #장애물로 가로막혀 있다고 판단할때, server로 전송하는 정보
                if len(obstacleAngle) >= 100 :
                    print('Stop move Stop move Stop move Stop move Stop move')
                    stopmove += 1

                # obstacle의 끝점 인식하기 #

                obstacle_sideAngle = []
                obstacle_centerAngle = []
                obstacle_centerDistance = []
                obstacle_sideDistance = []
                # obstacleDistance 및 obstacleAngle list의 [0]번째 요소는 모든 장애물의 양 끝점이라고 판단하고 sideDistance에 추가
                obstacle_sideAngle.append(obstacleAngle[0])
                obstacle_sideDistance.append(obstacleDistance[0])
                # obstacleAngle list에서 각도가 1도 이상 차이가 나면 다른 장애물이라고 판단하고 1도 차이가 나는 값의 각도, 거리를 끝점 list에 저장
                for m in range(1,len(obstacleAngle)):
                    # seperateObstacleRange만큼 차이가 나면 다른 객채라고 생각해서 분리
                    separateAngle = abs(obstacleAngle[m] - obstacleAngle[m-1])
                    separateDistance = abs(obstacleDistance[m]-obstacleDistance[m-1])
                    # 두 각도 간의 차이가 2도 이상이고, 떨어진 거리가 0.2m 보다 클때 두 요소는 하나의 장애물의 끝점이라고 판단
                    if separateAngle >= separateAngleRange and separateDistance >= separateDistanceRange:
                        obstacle_sideAngle.append(obstacleAngle[m-1])
                        obstacle_sideAngle.append(obstacleAngle[m])
                        # 1도 이상 차이가 나는 장애물의 거리값 list에 추가
                        obstacle_sideDistance.append(obstacleDistance[m - 1])
                        obstacle_sideDistance.append(obstacleDistance[m])
                    # 두 점 간의 각도가 2도보다 작지만 거리가 0.5m 이상일 때, 두 요소는 사나의 장애물의 끝점이라고 판단
                    elif separateAngle <= separateAngleRange and separateDistance >= separateDistanceRange + 0.2:
                        obstacle_sideAngle.append(obstacleAngle[m - 1])
                        obstacle_sideAngle.append(obstacleAngle[m])
                        # 1도 이상 차이가 나는 장애물의 거리값 list에 추가
                        obstacle_sideDistance.append(obstacleDistance[m - 1])
                        obstacle_sideDistance.append(obstacleDistance[m])
                    # 두 점간의 거리는 0.2m 보다 작지만, 각도 차이가 5도 이상일 떄, 두 요소는 하나의 장애물의 끝점이라고 판단
                    elif separateDistance <= separateDistanceRange and separateAngle >= separateAngleRange + 3:
                        obstacle_sideAngle.append(obstacleAngle[m - 1])
                        obstacle_sideAngle.append(obstacleAngle[m])
                        # 1도 이상 차이가 나는 장애물의 거리값 list에 추가
                        obstacle_sideDistance.append(obstacleDistance[m - 1])
                        obstacle_sideDistance.append(obstacleDistance[m])
                    # seperateObstacleRange만큼 차이가 나지 않으면 하나의 장애물이라고 판단하고 center list에 각도및 거리 추가
                    else:
                        obstacle_centerAngle.append(obstacleAngle[m])
                        obstacle_centerDistance.append(obstacleDistance[m])
                # obstacleDistance 및 obstacleAngle list의 [len(onstacleAngle) -1] 번째 요소는 모든 장애물의 양 끝점이라고 판단하고 sideDistance에 추가
                obstacle_sideAngle.append(obstacleAngle[len(obstacleAngle)-1])
                obstacle_sideDistance.append(obstacleDistance[len(obstacleAngle)-1])
                print('obstacle_sideAngle',obstacle_sideAngle)
                print('obstacle_sideDistacne',obstacle_sideDistance)

                CWKIM_dangerZone = []
                for danger in range(0, len(obstacle_sideAngle), 2):
                    CWKIM_angleDiff = obstacle_sideAngle[danger + 1] - obstacle_sideAngle[danger]
                    if (CWKIM_angleDiff > 30):
                        CWKIM_dangerZone.append(obstacle_sideAngle[danger])
                        CWKIM_dangerZone.append(obstacle_sideAngle[danger + 1])

                sideX = []
                sideY = []
                # 장애물 사이점을 계산하기 위해 위에서 판단한 sideAngle을 좌표계에 변환
                for o in range(0, len(obstacle_sideAngle)):
                    sideX.append(float(obstacle_sideDistance[o]) * math.cos(math.radians(90 - obstacle_sideAngle[o])))
                    sideY.append(float(obstacle_sideDistance[o]) * math.sin(math.radians(90 - obstacle_sideAngle[o])))
                #print('sideX', sideX)
                #print('sideY', sideY)
                # path 계산하는 부분 #
                pathAngle = []
                pathDistance = []
                after_pathAngle = []
                after_pathDistance = []
                betweenInformationlist = []
                sidePath_distanceRange = 0.65

                # 앞서 모든 장애물의 맨 왼쪽과 오른쪽 값이라고 판단한 값들의 경로 계산
                # sideAngle의 시작과 끝점으로 계산한 경로의 값이 -90˚ ~ 90˚ 내에 있을 때만 경로로 판단
                #print('obstacleSideangle_start',(obstacle_sideAngle[0] - sidePath_angleRange))
                #print('obstacleSideangleend', (obstacle_sideAngle[len(obstacle_sideAngle)-1] + (sidePath_angleRange + 5)))
                # sideAngle의 시작과 끝점은 맨 왼쪽, 오른쪽 끝점이라고 생각하고, sidePath_distanceRange 만큼 빼고 더해서 경로를 계산
                pathAngle.append(90 -(math.degrees(math.atan2(sideY[0],(sideX[0] - sidePath_distanceRange ))))) #m
                pathAngle.append(90 -(math.degrees(math.atan2(sideY[len(sideX) -1],(sideX[len(sideX) -1] + sidePath_distanceRange ))))) #m

                # 계산한 경로를 장애물의 바로 옆이 아닌 조금 앞에 찍어 장애물을 확실하게 피할 수 있게 지정
                pathDistance.append(math.sqrt((sideX[0] - sidePath_distanceRange) **2 + sideY[0]**2))
                pathDistance.append(math.sqrt((sideX[len(sideX)-1] + sidePath_distanceRange) **2 + sideY[len(sideX)-1]**2))

                # 변환한 sideX, sideY를 이용해 장애물 사이의 거리를 계산
                for m in range(1,len(sideX)-1,2):
                    betweenDistance = math.sqrt((sideX[m]-sideX[m+1])**2 + (sideY[m]-sideY[m+1])**2)
                    betweenAngle = obstacle_sideAngle[m + 1] - obstacle_sideAngle[m]
                    #print('betweenDistance : ', betweenDistance)
                    # print('betweenDistance',betweenDistance)
                    # 장애물 사이의 거리가 지정한 범위보다 작을때, 배가 지나갈 수 없다고 판단
                    # 장애물 사이의 각도가 지정한 범위보다 클 때, 배가 지나갈 수 없다고 판단
                    print('betweenDistance : ', betweenDistance)
                    print('betweenAngle : ', betweenAngle)

                    if betweenDistance < betweenDistance_range or betweenAngle < betweenAngle_range:
                        print('betweenDistance over range betweenDistance over range betweenDistance over range')
                        # 배가 지나갈 수 없다고 판단하여 경로 list에 추가할 값을 하지 않게 다음 반복문 진행
                        continue
                    # 장애물 사이의 거리 및 각도가 배가 지나갈 수 있다고 판단 될 때, 경로 list에 추가할 값을 계산
                    print('m:', m)
                    pathAngle.append(obstacle_sideAngle[m] + ((obstacle_sideAngle[m+1] - obstacle_sideAngle[m])/2))
                    pathDistance.append((obstacle_sideDistance[m]+obstacle_sideDistance[m+1])/2)

                # print('obstacle_sideAngle', obstacle_sideAngle)
                # print('betweenInformation', betweenInformationlist)
                # print('len(betweenInformation)', len(betweenInformationlist))
                # print('len(obstalce_sideAngle) -2',len(obstacle_sideAngle) -2)
                sidePath_XdistanceRange = 0.65
                sidePath_YdistanceRange = 0


                for g in range(1, len(obstacle_sideAngle)-2):
                    # 배로 부터 가깝고 사이 각도가 40도 이상인 모든 장애물의 side 에 sidePath_distanceRange 를 더하고 뺀 값을 path에 추가
                    if obstacle_sideDistance[g] < nearObstacleRange:
                        # 장애물의 왼쪽 끝점은 짝수번째 끝점이라고 생각해서 짝수번째 끝점은 0.5m 를 빼서 계산

                        CWKIM_pathAngle = 0

                        if g % 2 == 0:
                            CWKIM_pathAngle = 90 - (math.degrees(math.atan2(sideY[g] - sidePath_YdistanceRange, (sideX[g] - sidePath_XdistanceRange))))
                        else:
                            CWKIM_pathAngle = 90 - (math.degrees(math.atan2((sideY[g] + sidePath_YdistanceRange), (sideX[g] + sidePath_XdistanceRange))))

                        CWKIM_safeBool = True

                        print('pathAngle CWKIM ', CWKIM_pathAngle)
                        for danger in range(0, len(CWKIM_dangerZone), 2):
                            if (CWKIM_pathAngle > CWKIM_dangerZone[danger] - dangerZoneRange) and (CWKIM_pathAngle < CWKIM_dangerZone[danger + 1] + dangerZoneRange):
                                CWKIM_safeBool = False

                        if CWKIM_safeBool == False:
                            continue

                        if g % 2 == 0:
                            pathAngle.append(90 - (math.degrees(math.atan2(sideY[g], (sideX[g] - sidePath_XdistanceRange)))))
                            pathDistance.append(math.sqrt((sideX[g] - sidePath_XdistanceRange) ** 2 + (sideY[g]) ** 2))

                        # 장애물의 오른쪽 끝점은 홀수번째 끝점이라고 생각해서 홀수번째 끝점은 0.5m 를 더해서 계산
                        else:
                            pathAngle.append(90 - (math.degrees(math.atan2((sideY[g]),(sideX[g] + sidePath_XdistanceRange)))))
                            pathDistance.append(math.sqrt((sideX[g] + sidePath_XdistanceRange) ** 2 + (sideY[g]) ** 2))
                print('pathAngle',pathAngle)
                print('pathDistance', pathDistance)
                # 배가 가지 못하는 경로를 경로 list에서 제거하는 부분 #

                # print(len(pathAngle))
                # print(len(obstacle_sideAngle))
                # 모든 경로에 대해 배가 갈 수 있는 정보를 after_pathAngle 과 after_pathDistance 리스트에 추가

                for pat in range(0,len(pathAngle)):
                    after_check = 0
                    for ob in range(0, len(obstacle_sideAngle)-1, 2):
                        #print('pat',pat)
                        #print('ob',ob)
                        # 하나의 장애물 왼쪽 점보다 -5˚ 작은 값보다 계산한 경로값이 작거나 오른쪽 점보다 5˚ 큰 값보다 계산한 경로의 값이 더 크면 변수에 1을 더함
                        # 장애물과 겹치는 점을 제거하는 과정
                        if obstacle_sideAngle[ob] - checkAngle <= pathAngle[pat] <= obstacle_sideAngle[ob + 1] + checkAngle :
                            # print(obstacle_sideAngle[ob] - checkAngle, pathAngle[pat],obstacle_sideAngle[ob + 1] + checkAngle)
                            nearcheckDistanceleft = obstacle_sideDistance[ob] - checkDistance
                            nearcheckDistanceright = obstacle_sideDistance[ob + 1] - checkDistance
                            # print('checkAngle', checkAngle, 'checkDistance', checkDistance)
                            if nearcheckDistanceleft < 0 or nearcheckDistanceright < 0:
                                nearcheckDistanceleft = 0
                                nearcheckDistanceright = 0

                            if nearcheckDistanceleft < pathDistance[pat] < 5 or nearcheckDistanceright < pathDistance[pat] < 5:
                                # print('checkdistance',checkDistance)
                                # print(nearcheckDistanceleft, pathDistance[pat], 5,nearcheckDistanceright, pathDistance[pat], 5)
                                print('path near obstacle so continue')
                                continue
                        if abs(pathAngle[pat]) > 60:
                            continue

                        after_check += 1
                    # 더한 변수의 합이 더한만큼의 합 일때, 지나갈 수 있는 경로라고 판단
                    print('after_check', after_check)
                    if after_check == len(obstacle_sideAngle) / 2:
                        print(pathAngle[pat],'pass ckeck')
                        after_pathAngle.append(pathAngle[pat])
                        after_pathDistance.append(pathDistance[pat])
                print('after_pathAngle:', after_pathAngle)
                print('after_pathDistance:', after_pathDistance)

                    # server로 넘길 경로를 계산하는 부분 #

                    # 계산한 경로가 조건과 맞지 않아 하나도 list에 남아있지 않을때, 선택하는 경로
                if len(after_pathAngle) == 0 or stopmove != 0:
                    print('no path no path no path no path no path no path no path')
                    if obstacle_sideDistance[0] > obstacle_sideDistance[len(obstacle_sideDistance)-1] :
                        angle_to_server = obstacle_sideAngle[0] - sidePath_angleRange
                        distance_to_server = obstacle_sideDistance[0]
                    else:
                        angle_to_server = obstacle_sideAngle[len(obstacle_sideAngle)-1] + sidePath_angleRange
                        distance_to_server = obstacle_sideDistance[len(obstacle_sideAngle)-1]
                else:
                    # 모든 장애물이 한쪽으로 치우쳐져 있는지 판단하기 위해 obstacle_sideAngle list를 절댓값으로 치환하기 전과 후의 모든 요소를 더한 값을 비교
                    obstacle_sideAngle_abs = list(map(abs, obstacle_sideAngle))
                    after_pathAngle_abs = list(map(abs,after_pathAngle))
                    obstacle_sideAngle_sum = sum(obstacle_sideAngle)
                    obstacle_sideAngle_absSum = sum(obstacle_sideAngle_abs)
                    distance_to_server = 0
                    angle_to_server = 0
                    # 비교한 값이 같으면 모든 장애물이 한쪽으로 치우쳐져 있다고 판단후 직진
                    if abs(obstacle_sideAngle_sum) == obstacle_sideAngle:
                        print('go straight')
                        angle_to_server = 0
                        distance_to_server = 2
                    # 비교한 값이 다르면 모든 장애물이 한쪽으로 치우쳐져 있지 않다고 판단후 경로 추정
                    else:
                        print('go to path')
                        # 경로 중 가장 짧은 점까지의 거리가 1m 미만이고, 그때 각도가 -40˚ ~ 40˚ 사이면 가장 가까운 경로를 선정
                        if min(after_pathDistance) < 1 and min(obstacle_sideDistance) < 1:
                            angle_to_server = after_pathAngle[after_pathDistance.index(min(after_pathDistance))]
                            distance_to_server = after_pathDistance[after_pathDistance.index(min(after_pathDistance))]
                        # 경로가 가까이 있지 않을 때에는 가장 적게 회전하는 경로를 선정
                        else:
                            angle_to_server = after_pathAngle[after_pathAngle_abs.index(min(after_pathAngle_abs))]
                            distance_to_server = after_pathDistance[after_pathAngle_abs.index(min(after_pathAngle_abs))]

                # 계산한 경로의 각도가 음수면 좌회전을 출력, 양수면 우회전을 출력, 0이면 직진을 출력
                if angle_to_server <= 0:
                    if angle_to_server == 0:
                        print('Go stratighttttttttttttttttttttttttttttttttt')
                    else:
                        print('Turn LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLeft')
                else:
                    print('Turn RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRight')
                print(angle_to_server)
                print(distance_to_server)
                serverX = float(distance_to_server) * math.cos(math.radians(90 - angle_to_server))
                serverY = float(distance_to_server) * math.sin(math.radians(90 - angle_to_server))
                #print('serverX:',serverX)
                #print('serverY:',serverY)

                # 계산한 경로를 server로 전송하는 부분
                #PostLidarData(angle_to_server, distance_to_server, after_distanceList_to_server)

                #with open('/home/pi/00_ThrusterCode/data/lidarData.txt','w') as l:
                #   l.write(str(angle_to_server) +'\t'+ str(distance_to_server) +'\n' + str(after_distanceList_to_server) +'\n' + 'EOF')

                # raw data 로 좌표계에 인식한 물체를 표현
                rawX = []
                rawY = []
                for y in range(0, len(afterDistance)):
                    rawX.append(float(afterDistance[y]) * math.cos(math.radians(90 - rawAngle[y])))
                    rawY.append(float(afterDistance[y]) * math.sin(math.radians(90 - rawAngle[y])))
                # obstacleAngle, obstacleDistance 로 좌표계에 인식한 장애물을 표현
                obstacleX = []
                obstacleY = []
                for z in range(0, len(obstacleDistance)):
                    obstacleX.append(float(obstacleDistance[z]) * math.cos(math.radians(90 - obstacleAngle[z])))
                    obstacleY.append(float(obstacleDistance[z]) * math.sin(math.radians(90 - obstacleAngle[z])))
                pathX = []
                pathY = []
                for path in range(0, len(pathDistance)):
                    pathX.append(float(pathDistance[path]) * math.cos(math.radians(90 - pathAngle[path])))
                    pathY.append(float(pathDistance[path]) * math.sin(math.radians(90 - pathAngle[path])))
                afterPathX = []
                afterPathY = []
                for q in range(0, len(after_pathDistance)):
                    afterPathX.append(float(after_pathDistance[q]) * math.cos(math.radians(90 - after_pathAngle[q])))
                    afterPathY.append(float(after_pathDistance[q]) * math.sin(math.radians(90 - after_pathAngle[q])))
                checkX = []
                checkY = []
                x_values = []
                y_values = []
                XYcheckAngle = checkAngle
                XYcheckDistance = checkDistance
                for che in range(1, len(obstacle_sideAngle), 2):
                    checkX.append(float(obstacle_sideDistance[che - 1] - XYcheckDistance) * math.cos(
                        math.radians(90 - (obstacle_sideAngle[che - 1] - checkAngle))))
                    checkY.append(float(obstacle_sideDistance[che - 1] - XYcheckDistance) * math.sin(
                        math.radians(90 - (obstacle_sideAngle[che - 1] - checkAngle))))
                    checkX.append(5 * math.cos(math.radians(90 - (obstacle_sideAngle[che - 1] - checkAngle))))
                    checkY.append(5 * math.sin(math.radians(90 - (obstacle_sideAngle[che - 1] - checkAngle))))
                    checkX.append(float(obstacle_sideDistance[che] - XYcheckDistance) * math.cos(
                        math.radians(90 - (obstacle_sideAngle[che] + checkAngle))))
                    checkY.append(float(obstacle_sideDistance[che] - XYcheckDistance) * math.sin(
                        math.radians(90 - (obstacle_sideAngle[che] + checkAngle))))
                    checkX.append(5 * math.cos(math.radians(90 - (obstacle_sideAngle[che] + checkAngle))))
                    checkY.append(5 * math.sin(math.radians(90 - (obstacle_sideAngle[che] + checkAngle))))
                for ck in range(1, len(checkX), 2):
                    x_values.append([checkX[ck - 1], checkX[ck]])
                    y_values.append([checkY[ck - 1], checkY[ck]])
                print('checkX', checkX)
                print('checkY', checkY)
                print('x_values', x_values)
                print('y_values', y_values)
                print(len(x_values))

                # matplotlib 를 이용해서 좌표계에 인식한 값들을 시각화 하는 부분 #
                ax.clear()
                ax.plot(rawX, rawY, 'co')
                ax.plot(obstacleX, obstacleY, 'ro')
                # ax.plot(sideX, sideY,'bo')
                # ax.plot(sidePathX, sidePathY, 'yo')
                ax.plot(pathX, pathY, 'yo')
                ax.plot(afterPathX, afterPathY, 'go')
                ax.plot(serverX, serverY, 'bo')
                # for i in range(len(x_values) ):
                #    ax.plot(x_values[i], y_values[i], 'k-')
                ax.plot(0, 0, 'm*')
                ax.axis([-5, 5, -1, 6])

                # ax.plot(rawAngle, afterDistance, 'c', linestyle = 'solid')
                # ax.plot(obstacleAngle, obstacleDistance, 'ro')
                # ax.axis([-75, 75, -1, 11])

                ax.grid(True)
                plt.show()
                plt.pause(0.2)
            # 읽은 라이다 raw data 갯수가 360개가 아니면 해당 txt 파일을 읽어오지 않게 하는 부분

            else:
                continue

    # ctrl+c 로 코드를 끌 수 있게 하는 부분

    except KeyboardInterrupt:
        break


