from nmea import input_stream
import requests
import time
import os

################# dt ##################
totaldt = 0
start_time = time.time()
#####################################

dataStream = input_stream.GenericInputStream.open_stream("/dev/ttyACM0")
runOption = True

def PostGPSData(X, Y):
    UNAME = 'GPS'
    URL = 'http://192.168.2.12:9013/GPS'
    with open("/home/pi/00_ThrusterCode/data/gpsData.dat", "wt") as gpsFile:
        gpsFile.write(str(X) + "\t" + str(Y) + "\t" + str("EOF"))
        #gpsFile.write(str("EOF"))
    GPSFile_req = open("/home/pi/00_ThrusterCode/data/gpsData.dat", 'rb')
    GPSFile = {'GPSFile': GPSFile_req}
    reqData = {'uname': UNAME, 'fileName': GPSFile}
    try:
        res = requests.post(URL, files=GPSFile, data=reqData, timeout=0.1)
        GPSFile_req.close()
    except requests.exceptions.Timeout:
        PostGPSData(X, Y)

a = 0
fix = ("사용할수 없음", "기본값", "DGPS 보정", "fixed RTK  보정", "fixed RTK  보정X")

while runOption:
    try:
        ################# dt ##################
        end_time = time.time()
        dt = end_time - start_time
        start_time = end_time
        if dt > 1:
            dt = 0
        totaldt = dt + totaldt
        #####################################

        rawDataSet = dataStream.get_line()
        rawDataSet = str(rawDataSet, 'utf-8').strip("\r\n").split(",")

        if rawDataSet[0] == "$GNGGA":
            fixed = int(rawDataSet[6])

            if (0 < fixed <= 5):
                current_time = float(rawDataSet[1])  # 시간
                lat = float(rawDataSet[2])  # 위도
                lon = float(rawDataSet[4])  # 경도
                fixx = fix[fixed - 1]
            else:
                current_time = 0  # 시간
                lat = 0  # 위도
                lon = 0  # 경도
                fixx = 0

                print("*********************************")
                print("wrong signal")
                print("*********************************")

            #print(lat)
            #print(lon)

            ################## time ######################
            timehh = current_time // 10000
            timemm = current_time // 100 - timehh * 100
            timess = current_time - timehh * 10000 - timemm * 100

            ################## lat lon ######################
            lat_dd = int(lat // 100)
            lat_mm = lat - (lat_dd * 100)
            lat_mm = float(lat_mm) / 60
            lat = int(lat_dd) + float(lat_mm)

            lon_dd = int(lon // 100)
            lon_mm = lon - (lon_dd * 100)
            lon_mm = float(lon_mm) / 60
            lon = int(lon_dd) + float(lon_mm)

            ################## X,Y ######################
            ''' 
            #tournament
            y0 = 35.069631 #35.069688
            x0 = 128.578723 #128.578907
            x1 = 128.578669 #128.578795 # x끝
            y1 = 35.069610 #35.069656
            x2 = 128.578931#128.579037
            y2 = 35.069308 #35.069389

            X1 = 5
            Y1 = 0
            X2 = 0
            Y2 = 40
            
            '''
            #2
            y0 = 35.069688
            x0 = 128.578907
            x1 = 128.578795 # x끝
            y1 = 35.069656
            x2 = 128.579037
            y2 = 35.069389

            X1 = 10
            Y1 = 0
            X2 = 0
            Y2 = 40
            

            '''
            x0 = 128.96665446692
            y0 = 35.1150278968482
            x1 = 128.966755528754  # x끝
            y1 = 35.114863960063466666666666666666666666666
            x2 = 128.966846679444
            y2 = 35.1151124973373

            X1 = 20
            Y1 = 0
            X2 = 0
            Y2 = 19
            '''
            a = ((y2 - y0) * X1 - (y1 - y0) * X2) / ((y2 - y0) * (x1 - x0) - (y1 - y0) * (x2 - x0))
            b = ((x2 - x0) * X1 - (x1 - x0) * X2) / ((x2 - x0) * (y1 - y0) - (x1 - x0) * (y2 - y0))
            c = ((y2 - y0) * Y1 - (y1 - y0) * Y2) / ((y2 - y0) * (x1 - x0) - (y1 - y0) * (x2 - x0))
            d = ((x2 - x0) * Y1 - (x1 - x0) * Y2) / ((x2 - x0) * (y1 - y0) - (x1 - x0) * (y2 - y0))

            X = a * (lon - x0) + b * (lat - y0)
            Y = c * (lon - x0) + d * (lat - y0)

            ######### n ###########
            PostGPSData(X, Y)
            #######################

            print("*********************************")
            #print("time: ", int(timehh + 9), "h", int(timemm), "m", timess, "s")
            #print("Lat : ", round(lat, 3))
            #print("Lon : ", round(lon, 3))
            print('X : ', round(X, 3), 'Y : ', round(Y, 3))
            print("position fix: ", fixed, "(", fixx, ")")
            #print(dt)

    except KeyboardInterrupt:
        runOption = False
        gpsDataFile.close()
