from datetime import datetime
from pytz import timezone
from PIL import Image
import multiprocessing
from functools import partial
from multiprocessing import Process
print("Initialized at "+str(datetime.now(timezone('EST')))[11:19])
def runIteration(z,c,n):
    #iteration = lambda a : a**1.5 + c / (a+1)
    #original:
    #iteration = lambda a : a**a + (a/(c+complex(0.001,0.001)))
    iteration = lambda a : ( a**2 ) + c
    for i in range(n):
        try:
            z = iteration(z)
            if(str(z)=="(nan+nanj)"):
                print("YES")
                return -2
            if(z.real>100):
                return round(i/n*360)
        except OverflowError:
            return round(i/n*360)
    return -1

def pixelToComplex(x,y,Z,s,offset):
    return complex((((x -offset[0]- (s[0]/2))/s[0])/Z)*(s[0]/s[1]) ,((y -offset[1]- (s[1]/2))/s[1])/Z )

def setPixel(y,x,ratio,resolution,frame,zoom,offset):
    print("setpixel")
    return runIteration(inputA,pixelToComplex(x,y,zoom,frame,offset),360)

def returnImage(ratio,resolution,frame,zoom,offset):
    
    c = 0
    print(img)
    print("starting")
    temp = []
    pool = multiprocessing.Pool(12)
    for x in range(frame[0]):
        temp = (pool.map(partial(setPixel, x=x,ratio=ratio,resolution=resolution,frame=frame,zoom=zoom,offset=offset), [y for y in range(frame[1])]))
        
        
        if(c%((frame[0])/100)==0):
            print(str(round(c/(frame[0])*100))+" %")
        c+=1
    
        for y in range(len(temp)):
            if(temp[y]==-1):
                data[x,y] = (180-temp[y],0,0,)
            elif(temp[y]==-2):
                data[x,y] = (360,0,9999,)
            else:
                data[x,y] = (180-temp[y],200,200,)
        
            
    pool.close()
    pool.join()
    return img

ratio = [4,2]
resolution = 4
frame = [round(60*ratio[0]*resolution),round(60*ratio[1]*resolution)]
zoom = 0.4
#offset = [225,275]
#offset = [550,0]
#offset = [-5500,0]
#offset = [-9900,-300]
offset = [100,0]
offset[0] *= resolution*zoom
offset[1] *= resolution*zoom
img = Image.new('HSV', [frame[0],frame[1]], 255)
inputA = complex(0,0)
data = img.load()
if __name__=="__main__":
    returnImage(ratio,resolution,frame,zoom,offset).convert(mode="RGB").save('images/imageNew.png')
print("Saved at "+str(datetime.now(timezone('EST')))[11:19])
