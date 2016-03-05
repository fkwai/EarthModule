import sys,os,glob,datetime
import EarthModule
import EMFunc

shpfile=r"Y:\HUCs\HUC4_main_data_proj.shp"
HUCObj=EarthModule.EarthObj_vector("HUC4",shpfile,"HUC4")

tiffile=r"Y:\GRACE\geotiff\CLM4.LEAKAGE_ERROR.DS.G300KM.RL05.DSTvSCS1409.tif"
outRaster=r"Y:\GRACE\geotiff\GRACEref.tif"
#EarthModule.writeGRACEReftiff(tiffile,outRaster)
GRACEobj=EarthModule.EarthObj_raster("GRACE",outRaster)
filelist=glob.glob("Y:\GRACE\geotiff\*CSR*.tif")
i=0
for file in filelist[1:10]:
    print i
    i=i+1
    filename=os.path.splitext(os.path.basename(file))[0]
    datestr=filename.split(".")[2]
    date=datetime.datetime.strptime(str(datestr),"%Y%m%d").date()
    GRACEobj.addDataRaster(file,"GRACE",date)



SRTMfile=r"Y:\SRTM\srtm_19_06\srtm_19_06.tif"
SRTMfile2=r"Y:\SRTM\srtm_19_07\srtm_19_07.tif"
SRTMobj=EarthModule.EarthObj_raster("SRTM",SRTMfile,field="DEM")
clip,mask=EMFunc.clip(HUCObj.geometry[2], SRTMobj.geoTransform, SRTMobj.data["DEM"])

import gdal_merge as gm
file1=r"Y:\NED\n24w107\imgn24w107_1.img"
file2=r"Y:\NED\n25w107\imgn25w107_1.img"
file3=r"Y:\NED\n24w106\imgn24w106_1.img"
sys.argv = ['-o','outputfile.tiff',file1,file2,file3]
gm.main()

out_file="output.tif"
t_fh = gdal.Open( out_file, gdal.GA_Update )
gdal.PopErrorHandler()

