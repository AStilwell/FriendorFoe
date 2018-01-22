import math
import random

import global_cfg as cfg


# LOCAL PARAMETERS

def calc_originxy():
    temp = gps_to_xy(cfg.ORIGIN_LATITUDE, cfg.ORIGIN_LONGITUDE)
    cfg.BASE_X = temp[0]
    cfg.BASE_Y = temp[1]


def set_xy_ratio():
    temp = gps_to_xy(cfg.CORNER_LAT, cfg.CORNER_LONG)

    cfg.Y_RATIO = temp[1] / cfg.LENGTH_Y
    cfg.X_RATIO = temp[0] / cfg.LENGTH_X


def parse_gps_msg():
    """
    Gets the current GPS coordinates from the RC car. Currently generates a random GPS coordinate +/- error factor
    @return: Returns the lat, long, and altitude.
    """

    # $GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.5,M,46.9,M,,*47

    # 123519 = 12:35:19 UTC
    # 4807.038, N = 48 deg 07.038' N
    # 01131.000, E = 11 deg 32.000' E
    # 1 = Fix quality: 0 = invalid, 1 = GPS fix (SPS), 2 = DGPS fix, 3 = PPS fix, 4 = RTK fix, 5 = Float RTK,
    #       6 = estimated dead reckoning, 7 = manual input mode, 8 = simulation mode
    # 08 = Number of satellites being used
    # 0.9 = Horizontal dilution of position
    # 545.5, M = 545.4 M above mean sea-level
    # 46.9, M = 46.9 M above WGS84 ellipsoid
    # (empty) = Time in seconds since last DGPS update
    # (empty) = DGPS station ID number
    # *47 = checksum data, always begins with *

    # Test GGA message format from UBlox
    # $GPGGA,162254.00,3723.02837,N,12159.39853,W,1,03,2.36,525.6,M,-25.6,M,,*65
    # 74 ASCII characters, 74 byte message length

    # Insert method to poll GPS chips

    # message = poll_gps()

    # message = "$GPGGA,162254.00,3723.02837,N,12159.39853,W,1,03,2.36,525.6,M,-25.6,M,,*65"
    message = "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.5,M,46.9,M,,*47"

    separator = []

    for char in range(0, len(message)):
        if message[char] == ',':
            separator.append(char)

    print(separator)

    dlat = ''
    mlat = ''
    dlong = ''
    mlong = ''
    # altitude = ''

    # bytes 17 - 26
    print(message)
    for i in range(separator[1] + 1, separator[1] + 3):
        dlat = dlat + message[i]
    for j in range(separator[1] + 3, separator[2]):
        mlat = mlat + message[j]

    dlat = int(dlat)
    mlat = float(mlat)
    mlat = mlat / 60
    latitude = dlat + mlat

    if message[separator[2] + 1] == 'S':
        latitude = -latitude

    print(latitude)

    # bytes 30 - 40
    for k in range(separator[3] + 1, separator[3] + 4):
        dlong = dlong + message[k]
    for n in range(separator[3] + 4, separator[4]):
        mlong = mlong + message[n]

    dlong = int(dlong)
    mlong = float(mlong)
    mlong = mlong / 60
    longitude = dlong + mlong

    if message[separator[4] + 1] == 'W':
        longitude = -longitude

    print(longitude)

    data = scale_xy(gps_to_xy(latitude, longitude))

    return data


def test_poll_gps(flag, data):
    if flag:
        lat = (cfg.CORNER_LAT + cfg.ORIGIN_LATITUDE) / 2
        long = (cfg.CORNER_LONG + cfg.ORIGIN_LONGITUDE) / 2
    else:
        seed1 = random.random()
        seed2 = random.random()

        if seed1 >= 0.5:
            lat = data.LAT + random.uniform(0, cfg.NOISE)
        else:
            lat = data.LAT - random.uniform(0, cfg.NOISE)

        if seed2 >= 0.5:
            long = data.LONG + random.uniform(0, cfg.NOISE)
        else:
            long = data.LONG - random.uniform(0, cfg.NOISE)

        # while lat < cfg.ORIGIN_LATITUDE or lat > cfg.CORNER_LAT or long < cfg.ORIGIN_LONGITUDE or long > cfg.CORNER_LONG:
        #      seed1 = random.random()
        #      seed2 = random.random()
        #
        #      if seed1 >= 0.5:
        #          lat = data.LAT + random.uniform(0,0.0005)
        #      else:
        #          lat = data.LAT - random.uniform(0,0.0005)
        #
        #      if seed2 >= 0.5:
        #          long = data.LONG + random.uniform(0,0.0005)
        #      else:
        #          long = data.LONG - random.uniform(0,0.0005)

    return [lat, long]


def gps_to_xy(lat, long):
    """

    @param lat:
    @param long:
    @return:
    """

    radlat = math.radians(lat)
    radlong = math.radians(long)

    x = radlong - math.radians(cfg.ORIGIN_LONGITUDE)
    y = math.log(math.tan(radlat) + (1 / math.cos(radlat)))

    rot_x = x * math.cos(math.radians(cfg.ROTATION_ANGLE)) + y * math.sin(math.radians(cfg.ROTATION_ANGLE))
    rot_y = y * math.cos(math.radians(cfg.ROTATION_ANGLE)) - x * math.sin(math.radians(cfg.ROTATION_ANGLE))

    xy = [rot_x - cfg.BASE_X, rot_y - cfg.BASE_Y]
    # xy = [x - BASE_X, y - BASE_Y]

    return xy


def xy_to_gps(x, y):
    [x, y] = invert_xy([x, y])

    [x, y] = [x + cfg.BASE_X, y + cfg.BASE_Y]

    unrot_x = x * math.cos(math.radians(-cfg.ROTATION_ANGLE)) + y * math.sin(math.radians(-cfg.ROTATION_ANGLE))
    unrot_y = y * math.cos(math.radians(-cfg.ROTATION_ANGLE)) - x * math.sin(math.radians(-cfg.ROTATION_ANGLE))

    lat = math.atan(math.sinh(unrot_y))
    long = unrot_x + cfg.ORIGIN_LONGITUDE

    lat = math.degrees(lat)

    return (lat, long)


def scale_xy(xy):
    xy[0] = xy[0] / cfg.X_RATIO
    xy[1] = xy[1] / cfg.Y_RATIO

    return xy


def invert_xy(xy):
    xy[0] = xy[0] * cfg.X_RATIO
    xy[1] = xy[1] * cfg.Y_RATIO

    return xy

def deg_to_seconds(val):
    return val * 60 * 60


def gps_debug():
    calc_originxy()
    set_xy_ratio()

    # print(parse_gps_msg())
    # print("----------------")

    corner = gps_to_xy(cfg.CORNER_LAT, cfg.CORNER_LONG)
    print("*** Corner ***")
    print(corner)
    actxy = scale_xy(corner)
    print(actxy)

    print(xy_to_gps(actxy[0], actxy[1]))

    print("\n*** Center ***")
    center = gps_to_xy((cfg.ORIGIN_LATITUDE + cfg.CORNER_LAT) / 2, (cfg.ORIGIN_LONGITUDE + cfg.CORNER_LONG) / 2)
    print(center)
    print(scale_xy(center))

    print("\n*** Origin ***")
    origin = gps_to_xy(cfg.ORIGIN_LATITUDE, cfg.ORIGIN_LONGITUDE)
    print(origin)
    print(scale_xy(origin))

    print("\n*** Test ***")
    # testlat = input('Enter Test Latitude: ')
    # testlong = input('Enter Test Longitude: ')
    # test = gps_to_xy(float(testlat), float(testlong))

    test = gps_to_xy(29.190119, -81.046239)
    print(test)
    print(scale_xy(test))
