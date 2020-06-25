import numpy as np
from datetime import datetime
from pytz import timezone
from PIL import Image
import multiprocessing
from functools import partial
from multiprocessing import Process
print("Initialized at "+str(datetime.now(timezone('EST')))[11:19])
def runIteration(z,c,n):
	for i in range(n):
		try:
			z = iteration(z,c)
			if(str(z)=="(nan+nanj)"):
				#print("YES")
				return -2
				#return round(i/n*360)
			if(z.real>approximation or z.imag>approximation and approximate):
				return colorScaling(i,n)
		except Exception:
			return colorScaling(i,n)
	return -1

def colorScaling(i,n):
	if(coloring["scale"]=="linear"):
		return round((i/n)*360)
	if(coloring["scale"]=="logarithmic"):
		return round(float(( -1*( np.log( ( (-1*i)/n )+1 ) / np.log(n) ))*360))
		#return round(float(np.log((i/n)+1)*360))
	
	

def pixelToComplex(x,y,Z,s,offset):
    return complex((((x -offset[0]- (s[0]/2))/s[0])/Z)*(s[0]/s[1]) ,((y -offset[1]- (s[1]/2))/s[1])/Z )

def setPixel(y,x,ratio,resolution,frame,zoom,offset):
    print("setpixel")
    return runIteration(inputA,pixelToComplex(x,y,zoom,frame,offset),iterations)

def returnImage(ratio,resolution,frame,zoom,offset):
    
    c = 0
    print(img)
    print("starting")
    temp = []
    pool = multiprocessing.Pool(multiprocessing.cpu_count()-2)
    for x in range(frame[0]):
        temp = (pool.map(partial(setPixel, x=x,ratio=ratio,resolution=resolution,frame=frame,zoom=zoom,offset=offset), [y for y in range(frame[1])]))
        
        
        if(c%((frame[0])/100)==0):
            print(str(round(c/(frame[0])*100))+" %")
        c+=1
        
        
        if(coloring["inverted"]==1):
            inv=-1
        else:
            inv=1
        if(coloring["style"]=="color"):
            for y in range(len(temp)):
                if(temp[y]==-1):
                    data[x,y] = ((coloring["offset"]+(inv*temp[y]))%360,0,0,)
                elif(temp[y]==-2):
                    data[x,y] = (360,0,9999,)
                else:
                    data[x,y] = ((coloring["offset"]+(inv*temp[y]))%360,200,200,)
        elif(coloring["style"]=="monochrome"):
            for y in range(len(temp)):
                if(temp[y]==-1):
                    data[x,y] = (360,0,0,)
                else:
                    data[x,y] = (0,0,temp[y],)
    pool.close()
    pool.join()
    return img

# =======================
# ===START OF SETTINGS===
# =======================
print(multiprocessing.cpu_count()-2)
# -- iteration expression, with some other fun ones --
def iteration(a,c):
	return a**2 + c
	#return (a/np.sin(a-c))**(a/c) + c 
	#return a**a + ( a / ( c + complex(0.001,0.001) ) )
	#return a**2 + c**(a/c) 

coloring = {
	"style":"color",
	"scale":"linear",
	#180 is default blue, try 0 here with inverted color to 1 for orange
	"offset":0,
	#first value is if color is inverted, second if colors are swapped
	"inverted":[1,0]
	}

#approximation settings for faster computation
approximate = 1
approximation = 20

#how many iterations it will try on each pixel
iterations = 360

#image bounds, I recommend adjusting these with resolution set to a low number
#image size = 60*ratio*resolution
ratio = [4,3]
resolution = 6
zoom = 0.4
offset = [130,0]

# change of this can give interesting results. keep within (-1,-1) and (1,1)
inputA = complex(0,0)

# save location relative to where this script is run, as well as filename;
location = 'images/'
name = 'imageNew'
# =====================
# ===END OF SETTINGS===
# =====================

# sets up image
frame = [round(60*ratio[0]*resolution),round(60*ratio[1]*resolution)]
offset[0] *= resolution*zoom
offset[1] *= resolution*zoom
img = Image.new('HSV', [frame[0],frame[1]], 255)
data = img.load()
if __name__=="__main__":
    returnImage(ratio,resolution,frame,zoom,offset).convert(mode="RGB").save(location+name+'.png')
print("Saved at "+str(datetime.now(timezone('EST')))[11:19])
