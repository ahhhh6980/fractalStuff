

import math
from datetime import datetime
from pytz import timezone
from PIL import Image
import multiprocessing
from functools import partial
from multiprocessing import Process
print("Initialized at "+str(datetime.now(timezone('EST')))[11:19])
def runIteration(z,c,n):
	#iteration = lambda a : ( a**2 ) + c
	iteration = lambda a : a**a + ( a / ( c + complex(0.001,0.001) ) )
	for i in range(n):
		try:
			z = iteration(z)
			if(str(z)=="(nan+nanj)"):
				#print("YES")
				return -2
				#return round(i/n*360)
			if(z.real>20 or z.imag>20):
				return round(i/n*360)
		except Exception:
			return round(i/n*360)
	return -1


	#iteration = lambda a : a**1.5 + c / (a+1)
	#original:
	#iteration = lambda a : ( a**2 ) + c
	#z->z^z+(z/(c+(1+1i)))
	#toSin = lambda a : complex(math.sin(a.real),math.sin(a.imag))
	#testT = lambda a : complex(math.cos(a.real),math.sin(a.imag))
	
	#iteration = lambda a : a**2 + testT(c) 

def pixelToComplex(y,x,Z,s,offset):
	return complex((((x -offset[0]- (s[0]/2))/s[0])/Z)*(s[0]/s[1]) ,((y -offset[1]- (s[1]/2))/s[1])/Z )

def setPixel(y,x,ratio,resolution,frame,zoom,offset):
	
	color = runIteration(inputA,pixelToComplex(x,y,zoom,frame,offset),250)
	if(color==-1):
		data[x,y] = (180-color,0,0,)
	elif(color==-2):
		data[x,y] = (360,0,9999,)
	else:
		data[x,y] = (180-color,200,200,)

def returnImage(ratio,resolution,frame,zoom,offset):
	
	c = 0
	print(img)
	print("starting")
	temp = []
	pool = multiprocessing.Pool(1)
	for x in range(frame[0]):
		
		#print(pool.map(partial(setPixel, x=x,ratio=ratio,resolution=resolution,frame=frame,zoom=zoom,offset=offset), [y for y in range(frame[1])]))
		for y in range(frame[1]):
			setPixel(y,x,ratio,resolution,frame,zoom,offset)
		#except KeyboardInterrupt:
		#pool.close()
		#pool.terminate()
		#break
		#except Exception:
		#pool.close()
		#pool.terminate()
		
		if(c%((frame[0])/100)==0):
			print(str(round(c/(frame[0])*100))+" %")
		c+=1
	
		
	
	#pool.close()
	#pool.join()
	

ratio = [3,4]
resolution = 2
frame = [round(60*ratio[0]*resolution),round(60*ratio[1]*resolution)]
#zoom = 0.35
zoom=12
#zoom = 35
#offset = [225,275]
#offset = [550,0]
offset = [-10,-10]
#offset = [-9900,-300]
#offset = [90,0]
#offset = [-210,0]

#offset = [8,-3]

#offset = [0,0]
offset[0] *= (resolution/ratio[0])*(zoom)
offset[1] *= (resolution/ratio[1])*(zoom)
img = Image.new('HSV', [frame[0],frame[1]], 255)
inputA = complex(0,0)
data = img.load()
if __name__=="__main__":
	returnImage(ratio,resolution,frame,zoom/100,offset)
	img.convert(mode="RGB").save('images/imageNewest.png')
	
print("Saved at "+str(datetime.now(timezone('EST')))[11:19])
