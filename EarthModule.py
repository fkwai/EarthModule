import os
import gdal,ogr,fiona

class EarthObj(object):
    name=[]
    geo=[]
    geotype=[]
    geocount=[]

    def __init__(self,name,GISFile,IDfield=[]):
        self.name=name
        geo,geotype,geocount=InitGeo(GISFile, IDfield=[])
        self.geo=geo
        self.geotype=geotype
        self.geocount=geocount


def InitGeo(GISFile, IDfield=[]):
    filename,ext = os.path.splitext(GISFile)
    geo=[]
    geotype=[]
    geocount=[]
    if ext==".shp":
        geo=fiona.open(GISFile)
        geotype=geo[0]["geometry"]["type"]
        geocount=len(geo)
        if len(IDfield)!=0:
            ID=[int(geo[i]["properties"][IDfield]) for i in range(0,geocount)]

    return geo, geotype, geocount