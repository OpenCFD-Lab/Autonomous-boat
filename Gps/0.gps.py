from nmea import input_stream


dataStream = input_stream.GenericInputStream.open_stream("/dev/ttyACM0")
runOption = True

a=0
fix=("사용할수 없음", "기본값", "DGPS 보정", "fixed RTK  보정", "fixed RTK  보정X")

datagps = "/home/pi/00_ThrusterCode/data/gpsData.txt"
with open(datagps, "w") as gps_r:
#with open("j_gps_s.txt", "w") as gps_s:
    #gps_s.write("time(K)\tlat\tlong\tX\tY\tFIX" + '\n')

    while runOption:
        try:
            rawDataSet = dataStream.get_line()
            rawDataSet = str(rawDataSet, 'utf-8').strip("\r\n").split(",")

            if rawDataSet[0] == "$GNGGA":
                fixed = int(rawDataSet[6])

                if (0 < fixed <=5):

                    time = float(rawDataSet[1])  # 시간
                    lat = float(rawDataSet[2])  # 위도
                    lon = float(rawDataSet[4])  # 위도
                    fixx = fix[fixed-1]

                else:
                    time = 0  # 시간
                    lat = 0  # 위도
                    lon = 0  # 위도

                    fixx = 0

                    print("*********************************")
                    print("wrong signal")
                    print("*********************************")

                ################## time ######################
                timehh = time//10000
                timemm = time//100 - timehh*100
                timess = time - timehh*10000 - timemm*100
                #print(timehh)

                ################## lat lon ######################
                lat_dd = int (lat//100)
                lat_mm = lat - (lat_dd*100)
                lat_mm = float(lat_mm) / 60
                lat = int(lat_dd) + float(lat_mm)

                lon_dd = int (lon//100)
                lon_mm = lon - (lon_dd*100)
                lon_mm = float(lon_mm) / 60
                lon = int(lon_dd) + float(lon_mm)

                ################## X,Y ######################
                '''
                #tournament1
                y0 = 35.069631 #35.069688
                x0 = 128.578723 #128.578907
                x1 = 128.578669 #128.578795 # x끝
                y1 = 35.069610 #35.069656
                x2 = 128.578931#128.579037
                y2 = 35.069308 #35.069389
                
                X1 = 5#10
                Y1 = 0
                X2 = 0
                Y2 = 40#40
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

                a = ((y2 - y0) * X1 - (y1 - y0) * X2) / ((y2 - y0) * (x1 - x0) - (y1 - y0) * (x2 - x0))
                b = ((x2 - x0) * X1 - (x1 - x0) * X2) / ((x2 - x0) * (y1 - y0) - (x1 - x0) * (y2 - y0))
                c = ((y2 - y0) * Y1 - (y1 - y0) * Y2) / ((y2 - y0) * (x1 - x0) - (y1 - y0) * (x2 - x0))
                d = ((x2 - x0) * Y1 - (x1 - x0) * Y2) / ((x2 - x0) * (y1 - y0) - (x1 - x0) * (y2 - y0))

                X = a * (lon - x0) + b * (lat - y0)
                Y = c * (lon - x0) + d * (lat - y0)


                print("*********************************")
                print("time: ", int(timehh+9),"h", int(timemm),"m", timess,"s" )
                #print("Lat : ", lat)
                print("Lat : ", lat)#round(lat, 3))
                #print("Lon : ", lon)
                print("Lon : ", lon)#round(lon, 3))
                print('X : ', round(X, 3), 'Y : ', round(Y, 3))
                print("position fix: ", fixed,"(", fixx,")")


            #with open("j_gps_s.txt", "w") as gps_s:
                #gps_s.write(str(time) + " " + str(lat) + " " + str(lon)  + " " + str(X)  + " " + str(Y) + " " + str(lon) + " " + str(fixed) + " " + str(fixx) + " " + '\n')
                with open(datagps, "w") as gps_r:
                    gps_r.write(str(X) + "\t" + str(Y) + "\t")
                    gps_r.write("EOF")

        except KeyboardInterrupt:
            runOption = False
            gpsDataFile.close()
