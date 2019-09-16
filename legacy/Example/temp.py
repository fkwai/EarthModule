
import numpy

class test():
    a={}
    b=[]
    def __init__(self,a=None,b=[]):
        self.a["test"]=a
        self.b=b


a=numpy.zeros([2,2])
b=numpy.zeros([2,2])+1

t1=test(a=a,b=a)
t2=test(a=b,b=b)