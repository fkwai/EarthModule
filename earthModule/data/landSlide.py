
import pandas as pd
import earthModule
import earthModule.data
import os

dirData = earthModule.data.__path__[0]
fileTab = os.path.join(dirData, 'landSlideTab.csv')
df = pd.read_csv(fileTab)
lonRaw = df['DDLon'].tolist()
lon = [-float(x[:-1]) if x[-1] == 'W' else float(x[:-1]) for x in lonRaw]
latRaw = df['DDLat'].tolist()
lat = [-float(x[:-1]) if x[-1] == 'S' else float(x[:-1]) for x in lonRaw]
# date = df['Date'].tolist()
dateRaw = pd.to_datetime(df['Date']).tolist()
date=[x.to_pydatetime() for x in dateRaw]

'GE_39.667262_-105.280804_39.667973_-105.279188_20121007_PRE'
