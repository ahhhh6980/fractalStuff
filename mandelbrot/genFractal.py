import numpy as np
from datetime import datetime
from pytz import timezone
from PIL import Image
import multiprocessing
from functools import partial
from multiprocessing import Process
import dill
import pickle
print("Initialized at "+str(datetime.now(timezone('EST')))[11:19])
def runIteration(z,c,n,lamb,extra,coord):
	c = c + coord
	for i in range(n):
		try:
			if(unpackLambda):
				iterator = dill.loads(lamb)
				z = iterator(z,c,*extra)
			else:
				z = iteration(z,c)
			if(str(z)=="(nan+nanj)"):
				#print("YES")
				#return -2
				return colorScaling(i,n)
			#if(z.real>approximation or z.imag>approximation and approximate):
				#return colorScaling(i,n)
		except Exception:
			return colorScaling(i,n)
	return -1

def colorScaling(i,n):
	if(coloring["scale"]=="linear"):
		return round((i/n)*360)
	if(coloring["scale"]=="logarithmic"):
		return round(float(( -1*( np.log( ( (-1*i)/n )+1 ) / np.log(n) ))*360))
		#return round(float(np.log((i/n)+1)*360))

def pixelToComplex(x,y,zoom,scale):
	return complex( (((x - (scale[0]/2))/scale[0])/zoom)*(scale[0]/scale[1]), ((y - (scale[1]/2))/scale[1])/zoom )

def setPixel(y,x,ratio,resolution,frame,zoom,inp,lamb,extra,iterations,coord):
	return runIteration(inp,pixelToComplex(x,y,zoom,frame),iterations,lamb,extra,coord)

def generateImage( ratio, resolution, frame, zoom, inp, lamb, extra, iterations, coord):
	#initialize important values and print image information 
	temp = []
	rowCount = 0
	print(img)
	# establishes process pool
	pool = multiprocessing.Pool( multiprocessing.cpu_count() - excludeCores )
	print("Starting")
	for x in range( frame[0] ):
		#
		
		temp = (   pool.map(  partial( setPixel, x=x, ratio=ratio, resolution=resolution, frame=frame, zoom=zoom, inp=inp, lamb=lamb, extra=extra, iterations=iterations, coord=coord ), [ y for y in range(frame[1]) ]  )   )
		#
		if(  rowCount%( (frame[0])/updates ) == 0  ):
			print( str(  round( rowCount / (frame[0]) * 100 )  )+" %" )
		rowCount+=1
		#
		
		if( coloring["inverted"][0] == 1 ):
			inv=1
		else:
			inv=-1
		#
		if( coloring["style"] == "color" ):
			for y in range( len(temp) ):
				if( temp[y]==-1 ):
					data[x,y] = ( (coloring["colorLoops"]*(coloring["offset"] + round(coloring["colorScale"] * (  (inv*temp[y]) ))))%360, 0, 0,  )
				elif( temp[y]==-2 ):
					data[x,y] = ( 360, 0, 0, )
				else:
					data[x,y] = ( (coloring["colorLoops"]*(coloring["offset"] + round(coloring["colorScale"] * (  (inv*temp[y]) ))))%360, round(256/coloring["desaturation"]), 256,  )
		#
		elif( coloring["style"] == "monochrome" ):
			for y in range(len(temp)):
				if(temp[y]==-1 ):
					data[x,y] = (360,0,(360*coloring["inverted"][0]),)
				else:
					data[x,y] = (0,0,round(temp[y]*coloring["colorScale"]+(360*coloring["inverted"][0]))%360,)
	#
	pool.close()
	pool.join()

# =======================
# ===START OF SETTINGS===
# =======================

#specify cores to be excluded from multiprocessing;
excludeCores = 2
print(str(multiprocessing.cpu_count()-excludeCores)+" cores")

# -- iteration expression, with some other fun ones --
#iterationLamb = a**2+c
def iteration(a,c):
	return a**2+c
	#return (a/np.sin(a-c))**(a/c) + c 
	#return np.cos(a)**a*2 + ( np.sin(a) / ( c + complex(0.00001,0.00001) ) )
	#return a**2 + c**(a/c) 

#styles include; "monochrome" and "color"
#scales include; "linear" and "logarithmic"
coloring = {
	"style":"color",
	"scale":"linear",
	#180 is default blue, try 0 here with inverted color to 1 for orange
	"offset":0,
	#first value is if color is inverted, second if colors are swapped
	"inverted":[1,0],
	#color scale before offset is applied
	"colorScale":1.5 ,
	#number between 1 and 256; 256 being just pure white, and 1 being pure vibrant
	"desaturation":1.1,
	#color scale after offset is applie
	"colorLoops":1
	}
#coloring["colorLoops"]

#approximation settings for faster computation, not really needed for anything smaller than 1920x1080
approximate = 0
approximation = 1000

#how many iterations it will try on each pixel
iterationCount = 360

#image bounds, I recommend adjusting these with resolution set to a low number
#image size = 60*ratio*resolution
#I advise against setting resolution to anything above 5 or 10
ratio = [4,3]
resolution = 10
zoom = 0.4

#coordinates = [-0.75,0.1]
coordinates = [-0.7,0]
# change of this can give interesting results. keep within (-1,-1) and (1,1)
layerc = complex(0,0)

# save location relative to where this script is run, as well as filename;
location = 'test2/'
name = 'gen2'

# logging settings;
updates = 20

#misc
xLayers = 360
unpackLambda = False
layer = 0

#((x - (xLayers/2))/(xLayers/2))*1

#((i - (xLayers/2))/(xLayers/2))

# =====================
# ===END OF SETTINGS===
# =====================

# sets up image
frame = [ round( 60*ratio[0]*resolution ), round( 60*ratio[1]*resolution ) ]

img = Image.new( 'HSV', [ frame[0], frame[1] ], 255 )
data = img.load()

def outputImage(z,count,lamb,extra, iterations, coord):
	generateImage( ratio, resolution, frame, zoom, z, lamb, extra, iterations, coord )
	#img.convert( mode="RGB" ).save( location+name+"["+str(z.real)+","+str(z.imag)+"]"+'.png' )
	img.convert( mode="RGB" ).save( location+name+"_"+str(count)+'.png' )


if __name__=="__main__":
	"""
	for x in range(xLayers):
		print(" ")
		print(complex( 3*((x - (xLayers/2))/(xLayers/2)) ,layer ))
		print(" ")
		print(str(x)+" "+"started")
		#outputImage( complex( 2.67*((x - (xLayers/2))/(xLayers/2)) ,2.67*((x - (xLayers/2))/(xLayers/2)) ), x )
		outputImage(layerc, x)
		print(str(x)+" "+"finished")
		print(" ")
	"""
	"""
	for i in range(360):
		print(" ")
		print(((i/100)*3)+2)
		print(" ")
		outputImage(layerc,i,dill.dumps(lambda a,c,e,d : a**(e+d) + c),((i/100)*3,2))
	"""
	#unpackLambda = False
	#for i in range(360):
		#outputImage(layerc, i, dill.dumps(lambda a,c,e,d : a**(e+d) + c),(2,0), i+10)
	outputImage(layerc, 0, dill.dumps(lambda a,c,e,d : a**(e+d) + c),(2,0), iterationCount, complex(coordinates[0],-1*coordinates[1]))

print("Saved at "+str(datetime.now(timezone('EST')))[11:19])
