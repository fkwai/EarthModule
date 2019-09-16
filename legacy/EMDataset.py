import math,os



def NEDindex(VectorObj,NEDpath=None):
    #find index of NED. Return a list of NED index of all features in VectorObj
    indNorth=[]
    indWest=[]
    NEDfile=[]
    for geo in VectorObj.getGeometry():
        bb=geo.GetEnvelope()
        x1=bb[0]
        x2=bb[1]
        y1=bb[2]
        y2=bb[3]
        indx1=int(-math.floor(x1))
        indx2=int(-math.floor(x2))
        indy1=int(math.ceil(y1))
        indy2=int(math.ceil(y2))
        indWesttemp=range(indx2,indx1+1)
        indNorthtemp=range(indy1,indy2+1)
        indNorth.append(indNorthtemp)
        indWest.append(indWesttemp)
        if NEDpath is not None:
            NEDfiletemp=[]
            for indN in indNorthtemp:
                for indW in indWesttemp:
                    tempfile=NEDpath+"\\"+"n%02iw%03i"%(indN,indW)+"\\"+\
                             "imgn%02iw%03i_1.img"%(indN,indW)
                    if os.path.exists(tempfile):
                        NEDfiletemp.append(tempfile)
                    else:
                        print("no file for n%02iw%03i"%(indN,indW))
            NEDfile.append(NEDfiletemp)
    return NEDfile,indNorth,indWest

def NED2VectorObj(STRMpath,VectorObj,option=0):
    pass