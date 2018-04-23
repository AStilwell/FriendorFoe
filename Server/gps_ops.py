import math

import server_cfg as cfg

# import random

BASE_X = 0
BASE_Y = 0
X_RATIO = 1
Y_RATIO = 1


class GPSCalculations:

    def __init__(self, debug):
        self.debug = debug
        if debug:
            print('******INITIALIZED GPS******')

    def parse_gps_msg(self, message):
        """
        Parses a GGA formatted string and returns the lat and long in degree-decimal format

        :param message: <String> the GGA message that is to be parsed, a string
        :return: <Array> a two element array that contains the lat and long
        """
        message = '$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,,230394,003.1,W*6A'

        separator = []

        for char in range(0, len(message)):
            if message[char] == ',':
                separator.append(char)

        if self.debug:
            print("Separator: ", separator)

        dlat = ''
        mlat = ''
        dlong = ''
        mlong = ''
        headingstr = ''

        # bytes 17 - 26
        if self.debug:
            print("GPS Message: ", message)
        for i in range(separator[2] + 1, separator[2] + 3):
            dlat = dlat + message[i]
        for j in range(separator[2] + 3, separator[3]):
            mlat = mlat + message[j]

        dlat = int(dlat)
        mlat = float(mlat)
        mlat = mlat / 60
        latitude = dlat + mlat

        if message[separator[3] + 1] == 'S':
            latitude = -latitude

        if self.debug:
            print("Latitude: ", latitude)

        # bytes 30 - 40
        for k in range(separator[4] + 1, separator[4] + 4):
            dlong = dlong + message[k]
        for n in range(separator[4] + 4, separator[5]):
            mlong = mlong + message[n]

        dlong = int(dlong)
        mlong = float(mlong)
        mlong = mlong / 60
        longitude = dlong + mlong

        if message[separator[5] + 1] == 'W':
            longitude = -longitude

        if self.debug:
            print("Longitude: ", longitude)

        data = self.scale_xy(self.gps_to_xy(latitude, longitude))

        if separator[7] + 1 == separator[8]:
            headingstr = '999'
        else:
            for l in range(separator[7] + 1, separator[7] + 5):
                headingstr = headingstr + message[l]

        heading = float(headingstr)

#       xposition = random.randint(0, cfg.LENGTH_X)
#       yposition = random.randint(0, cfg.LENGTH_Y)

#       data = [xposition, yposition]

        print(data, heading)
        return data, heading

    @staticmethod
    def gps_to_xy(lat, lon):
        """
        Converts the lat, long to a raw x,y value based on the reference points in the config file

        :param lat: <Float> decimal latitude value
        :param lon: <Float> decimal longitiude value
        :return: <Array> two element array consisting of raw x,y values
        """

        radlat = math.radians(lat)
        radlong = math.radians(lon)

        x = radlong - math.radians(cfg.ORIGIN_LONGITUDE)
        y = math.log(math.tan(radlat) + (1 / math.cos(radlat)))

        rot_x = x * math.cos(math.radians(cfg.ROTATION_ANGLE)) - y * math.sin(math.radians(cfg.ROTATION_ANGLE))
        rot_y = y * math.cos(math.radians(cfg.ROTATION_ANGLE)) + x * math.sin(math.radians(cfg.ROTATION_ANGLE))

        xy = [rot_x - BASE_X, rot_y - BASE_Y]

        return xy

    def scale_xy(self, xy):
        """
        Scales xy values to proper size based on length and width of field

        :param xy: <Array> vector to be scaled (x,y)
        :return: <Array> two element array consisting of scaled x,y values
        """
        self.set_xy_ratio()

        xy[0] = xy[0] / X_RATIO
        xy[1] = xy[1] / Y_RATIO

        return xy

    @staticmethod
    def deg_to_seconds(val):
        """
        Converts degrees to seconds (1 degree = 60 minutes = 3600 seconds)

        :param val: <Float> value to be converted
        :return: <Float> converted value
        """
        return val * 60 * 60

    def gps_debug(self):
        """
        Debug function for GPS

        :return: <Int> 0 on success
        """
        self.calc_originxy()
        self.set_xy_ratio()

        print(self.parse_gps_msg(''))
        print("----------------")

        corner = self.gps_to_xy(cfg.CORNER_LAT, cfg.CORNER_LONG)
        print("*** Corner ***")
        print(corner)
        print(self.scale_xy(corner))

        print("\n*** Center ***")
        center = self.gps_to_xy(
            (cfg.ORIGIN_LATITUDE + cfg.CORNER_LAT) / 2,
            (cfg.ORIGIN_LONGITUDE + cfg.CORNER_LONG) / 2
        )
        print(center)
        print(self.scale_xy(center))

        print("\n*** Origin ***")
        origin = self.gps_to_xy(cfg.ORIGIN_LATITUDE, cfg.ORIGIN_LONGITUDE)
        print(origin)
        print(self.scale_xy(origin))

        print("\n*** Test ***")
        testlat = input('Enter Test Latitude: ')
        testlong = input('Enter Test Longitude: ')
        test = self.gps_to_xy(float(testlat), float(testlong))
        print(test)
        print(self.scale_xy(test))

        return 0

    def calc_originxy(self):
        """
        Calculates origin x,y based on latitude and longitude. Used to laterally shift the x,y to 0,0.

        :return: <Array> Base X and Y values
        """
        global BASE_X
        global BASE_Y

        temp = self.gps_to_xy(cfg.ORIGIN_LATITUDE, cfg.ORIGIN_LONGITUDE)
        BASE_X = temp[0]
        BASE_Y = temp[1]

        return BASE_X, BASE_Y

    def set_xy_ratio(self):
        """
        Calculate the XY ratio based on the length and width versus the change in lat/long between origin and diagonal
        corner

        :return: <Array> Calculated X and Y Ratio
        """
        global X_RATIO
        global Y_RATIO

        temp = self.gps_to_xy(cfg.CORNER_LAT, cfg.CORNER_LONG)
        Y_RATIO = temp[1] / cfg.LENGTH_Y
        X_RATIO = temp[0] / cfg.LENGTH_X

        return X_RATIO, Y_RATIO

    @staticmethod
    def request_gps_fix(connection):
        connection.client_tx('gps')


test = GPSCalculations(True)
test.parse_gps_msg('')
