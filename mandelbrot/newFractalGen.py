import math
import numpy as np
import multiprocessing
from decimal import *
from PIL import Image
import datetime

# Functions
def log(b,x): 
    try:
        return(np.log(x)/np.log(b))
    except Exception:
        return 0

# Map i from range a to range b
def mapRange( i, a, b ): return (( i - a[0] ) / a[1]) * (b[1] - b[0]) + b[0]
# Above but more complex, outputs exponentially to value e
def scaleToRangeSimple( i, a, b, e ):
    return (np.power(  i - a[0], ( e + log(i - a[0], b[1] - b[0]) )  ) / np.power(a[1] - a[0], e) + b[0] )

def getTime(): return ("{"+str(now.hour)+"h:"+str(now.minute)+"m:"+str(now.second)+"."+str(now.microsecond)+"s}")

def split( ):
    temp = []
    for y in range(frame[1]):
        for x in range(frame[0]): temp.append([x,y])
    return temp

# Setup
ratio = [1,1]
# Be careful, high resolutions take a LOT of ram
# For 16:9, 5 gives you a 4800px X 2700px image, which may require up to or over 16gb of ram
resolution = 10
frame = [ round( 60*ratio[0]*resolution ), round( 60*ratio[1]*resolution ) ]
img = Image.new( 'HSV', [ frame[0], frame[1] ], (100,0,360) )
data = img.load()

# Processing
# WARNING: SET THIS APPROPRIATELY TO YOUR SYSTEM
availableCores = 10
colorExponent = 0.5

#zoom = 0.4
#zoom = 1
zoom = 0.7
pLimit = 2500
l = pLimit
#position = complex(2,1.5)
#position = complex(-0.2045,0.2510)
position = complex(-0.25,0.5)
isMandelbrot = True

# Computation function
def computePixel( pixel ):
    c = (complex( mapRange( pixel[0] , [0,frame[0]], [-1,1] )/zoom, (frame[1]/frame[0])*mapRange( pixel[1] , [0,frame[1]], [-1,1] )/zoom ) - (complex(0.5,0.5)-position))
    z = c
    p = np.sqrt((c.real-0.25)**2 + c.imag**2)

    # Exclude cardioid and main bulb
    if( (isMandelbrot==False) or (c.real > p - (2*(p**2)) + 0.25 and (c.real+1)**2 + (c.imag**2) >1/16) ):
        for i in range(l):
            try:
                if(isMandelbrot):
                    z = z**2 + c
                else:
                    z = z**z + ( z / ( c + complex(0.001,0.001) ) )
                if(str(z)=="(nan+nanj)"):
                    #print("YES")
                    return [pixel,[(scaleToRangeSimple(i,[0,l],[0,360],colorExponent)),i]]
                
            except Exception:
                #return ( mapRange( (pixel[0]/(pixel[1]+1))*i, [0,(frame[0]/frame[1])*l], [0,360] ) )
                return [pixel,[(scaleToRangeSimple(i,[0,l],[0,360],colorExponent)),i]]
    return [pixel,[-1,256]]
    #return -1"""

def getSplit( i, s):
    output = []
    temp = []
    for y in range(frame[1]):
        if( y ): pass
        for x in range(frame[0]):
            temp.append([x,y])
    return temp
    
# Saving Info
location = 'images/'
name = 'mandelbrotTest'
consoleReadouts = 5

if __name__=="__main__":
    start = datetime.datetime.now()
    now = start

    print("\nStarted {"+str(frame[0])+"px X "+str(frame[1]) +"px} at: "+getTime()+" with "+str(pLimit)+" i/px","\n")
    now = datetime.datetime.now()

    print("\nSTARTING MULTIPROCESSING\n@"+getTime())
    p = multiprocessing.Pool(availableCores)
    r = p.map(computePixel,split())
    p.close();p.join()
    i = 0
    now = datetime.datetime.now()

    print("\nSTARTING COLOR ASSIGNMENT\n@"+getTime())
    for e in r:
        i+=1
        color = e[1][0]
        x,y = e[0][0],e[0][1]
        if((i/(frame[0]*frame[1]) * 100)%int(100/consoleReadouts) == 0):
            now = datetime.datetime.now()
            print(str(int((i/(frame[0]*frame[1])) * 100))+"%","@ "+getTime(),"("+str(i)+"/"+str(frame[0]*frame[1])+")")
        if(color==-1):
            data[x,y] = (0,0,0)
        else:
            #int(e[1][1]/(1))
            data[x,y] = (int(((color*(2))+(45*3))%360), 256, int((e[1][1])**1.5))
    
    now = datetime.datetime.now() 
    print("\nSAVING IMAGE\n@"+getTime())
    img.convert( mode="RGB" ).save( location+name+"_"+str(14)+'.png' )

    now = datetime.datetime.now()
    d = now - start
    print("\nFinished in "+str(d.total_seconds())+" Seconds!")
    
