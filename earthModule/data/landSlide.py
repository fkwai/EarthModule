import pandas as pd
import earthModule
import os
import datetime


def readTabInfo(tabFile=None):
    dirData = earthModule.data.__path__[0]
    if tabFile is None:
        fileTab = os.path.join(dirData, 'landSlideData', 'landSlideTab.csv')
    df = pd.read_csv(fileTab)
    lonRaw = df['DDLon'].tolist()
    lon = [-float(x[:-1]) if x[-1] == 'W' else float(x[:-1]) for x in lonRaw]
    latRaw = df['DDLat'].tolist()
    lat = [-float(x[:-1]) if x[-1] == 'S' else float(x[:-1]) for x in latRaw]
    dateRaw = pd.to_datetime(df['Date']).tolist()
    date = [x.to_pydatetime() for x in dateRaw]
    return lat, lon, date


def readFileBound(fileName):
    # fileNamePre = 'GE_39.667262_-105.280804_39.667973_-105.279188_20121007_PRE''map.html')
    temp = fileName.split('_')
    x1 = float(temp[2])
    y1 = float(temp[1])
    x2 = float(temp[4])
    y2 = float(temp[3])
    bb = [y1, x1, y2, x2]
    return bb


def readFileDate(fileName):
    temp = fileName.split('_')
    tstr = temp[5]
    t = datetime.datetime.strptime(tstr, "%Y%m%d").date()
    return t
