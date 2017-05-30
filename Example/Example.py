import sys,os,glob,datetime,time
import EarthModule
import EMFunc,EMDataset
import numpy
import pickle

shpfile=r"Y:\HUCs\HUC4_main_data_proj.shp"
HUCObj=EarthModule.EarthObj_vector(name="HUC4",geofile=shpfile,IDfield="HUC4")
#
# tiffile=r"Y:\GRACE\geotiff\CLM4.LEAKAGE_ERROR.DS.G300KM.RL05.DSTvSCS1409.tif"
# outRaster=r"Y:\GRACE\geotiff\GRACEref.tif"
# #EarthModule.writeGRACEReftiff(tiffile,outRaster)
# GRACEobj=EarthModule.EarthObj_raster("GRACE",outRaster)
# filelist=glob.glob("Y:\GRACE\geotiff\*CSR*.tif")
# i=0
# for file in filelist[1:10]:
#     print i
#     i=i+1
#     filename=os.path.splitext(os.path.basename(file))[0]
#     datestr=filename.split(".")[2]
#     date=datetime.datetime.strptime(str(datestr),"%Y%m%d").date()
#     GRACEobj.addDataRaster(file,"GRACE",date)

NEDfile,indNorth,indWest=EMDataset.NEDindex(HUCObj,NEDpath=r"Y:\NED")
n=len(NEDfile)
ElevMean=[numpy.nan]*n
ElevStd=[numpy.nan]*n
SlopeMean=[numpy.nan]*n
SlopeStd=[numpy.nan]*n
errorBasin=[]

for i in range(len(NEDfile)):
    print("basin %i:"%(i+1))
    try:
        t1=time.clock()
        objList=[]
        for file in NEDfile[i]:
            obj=EarthModule.EarthObj_raster(geofile=file,field="NED")
            objList.append(obj)
        t2=time.clock()
        print("read data cost %f"%(t2-t1))

        t1=time.clock()
        mergeObj=EMFunc.merge(objList,"NED",date=0)
        t2=time.clock()
        print("merge data cost %f"%(t2-t1))

        t1=time.clock()
        poly=HUCObj.getGeometry()[i]
        clipObj,maskObj=EMFunc.clip(poly=poly,rasterObj=mergeObj,field="NED")
        t2=time.clock()
        print("clip data cost %f"%(t2-t1))

        t1=time.clock()
        slope=EMFunc.slope(rasterObj=clipObj,field="NED")
        t2=time.clock()
        print("slope calculation cost %f"%(t2-t1))

        elev=clipObj.getData("NED")
        ElevMean[i]=numpy.nanmean(elev)
        ElevStd[i]=numpy.nanstd(elev)
        SlopeMean[i]=numpy.nanmean(slope)
        SlopeStd[i]=numpy.nanstd(slope)

        del(mergeObj,clipObj,maskObj,slope)
    except:
        errorBasin.append(i)

EMFunc.writeCSV("DEM_HUC4.csv",[HUCObj.getID(),ElevMean,ElevStd,SlopeMean,SlopeStd])


    # clipObj.writeTiff(outfile="out.tif",field="NED")
    # clipObj.addData(data=slope,field="slope")
    # clipObj.writeTiff(outfile="out_slope.tif",field="slope")

#NLCD
shpfile=r"Y:\HUCs\HUC4_prj_NLCD.shp"
HUCObj=EarthModule.EarthObj_vector(name="HUC4",geofile=shpfile,IDfield="HUC4")
NLCDfile=r"Y:\NLCD\nlcd_2011_landcover_2011_edition_2014_10_10\nlcd_2011_landcover_2011_edition_2014_10_10.img"

t1=time.clock()
NLCDobj=EarthModule.EarthObj_raster(geofile=NLCDfile,field="NLCD",optNan=0)
t2=time.clock()
print("read data cost %f"%(t2-t1))

purban=[]
pforest=[]
for i in range(len(HUCObj.getGeometry())):
    print("basin %i:"%(i+1))
    t1=time.clock()
    poly=HUCObj.getGeometry()[i]
    clipNLCDObj,maskNLCDObj=EMFunc.clip(poly=poly,rasterObj=NLCDobj,field="NLCD",vNan=0)
    t2=time.clock()
    print("clip data cost %f"%(t2-t1))

    data=clipNLCDObj.getData("NLCD")
    n=numpy.count_nonzero(data).__float__()
    nurban=numpy.count_nonzero(numpy.logical_and(data>20,data<30)).__float__()
    nforest=numpy.count_nonzero(numpy.logical_and(data>40,data<50)).__float__()
    purban.append(nurban/n)
    pforest.append(nforest/n)

EMFunc.writeCSV("NLCD_HUC4.csv",[HUCObj.getID(),purban,pforest])
