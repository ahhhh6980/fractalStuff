import numpy as np
import multiprocessing
from PIL import Image, ImageOps
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

# for pre-generating
def split( ): return [[x,y] for x in range(frame[0]) for y in range(frame[1])]

availableCores = multiprocessing.cpu_count()

# Setup

# Coordinate on fractal image will be centered on
#position = complex(0.675,0.72)
#position = complex(2.8,-0.5)
position = complex(1.95,-0.25)
# If you want to angle the fractal
# Slightly slower rendering if value is not zero
# p offsets vertically and horizontally independant of rotation :)
theta = 0
angle = (theta*np.pi)/180
p = complex(-0.04, -0.05)
if(theta!=0):
    position += complex(p.real*np.cos(angle)+p.imag*np.sin(angle),(p.real)*np.sin(-angle)+p.imag*np.cos(angle))

zoom = 2

# Be careful, high resolutions take a LOT of ram
# For 16:9, 5 gives you a 4800px X 2700px image, which may require up to or over 8gb of ram
# resolution * 60 * ratio = image size
resolution = 20
ratio = [1,1]

# slight color adjustment
cScale = 0.25
cOffset = 45*0
colorExponent = 0.55
lightnessExponent = 1.2
lightnessScale = 1
# iteration limit
l=2500

# These can override settings
isMandelbrot = False
isBurningShip = True
isJulia = False
juliaCoord = complex(0.3,0.5)

if(isMandelbrot):
    l = 2500
    zoom = 0.7
    ratio = [4,3.5]
    position = complex(-0.25,0.5)

if(isJulia):
    zoom = 1
    position = complex(0.5,0.5)
    l = 2500
    colorExponent = 0.15 * (cScale/2)
    colorExponent = 1
    ratio = [3,3.5]

if(isBurningShip):
    colorExponent = 0.4
    zoom = 55
    ratio = [3,6]
    position = complex(-1.124,0.4685)

# Saving Info
location = 'images/'
name = 'mandelbrot'
consoleReadouts = 10
scaling = False

# Frame setting and image setup
frame = [ round( 60*ratio[0]*resolution ), round( 60*ratio[1]*resolution ) ]
img = Image.new( 'HSV', [ frame[0], frame[1] ], (100,0,360) )
data = img.load()

# Computation function
def computePixel( pixel ):
    c = (complex( mapRange( pixel[0] , [0,frame[0]], [-1,1] )/zoom, (frame[1]/frame[0])*mapRange( pixel[1] , [0,frame[1]], [-1,1] )/zoom ))
    if(theta!=0):
        c = complex(c.real*np.cos(angle)+c.imag*np.sin(angle),(-c.real)*np.sin(angle)+c.imag*np.cos(angle)) - (complex(0.5,0.5)-position)
    else:
        c -= (complex(0.5,0.5)-position)
    #z = ( c ** c )
    z = c
    #z = complex(0,0)
    p = np.sqrt((c.real-0.25)**2 + c.imag**2)
    m = 0
    # Exclude cardioid and main bulb
    # )
    temp = 12
    if(isJulia): c = juliaCoord
    if( isJulia or (isMandelbrot==False) or (isMandelbrot and ((c.real > p - (2*(p**2)) + 0.25 and (c.real+1)**2 + (c.imag**2) >1/16)))):
        for i in range(l):
            try:
                if(isMandelbrot and not(isBurningShip)):
                    #c = (c + (c/(i+1))/c)*0.5
                    z = z**2 + c
                elif(isBurningShip and not(isMandelbrot)):
                    z = complex(np.abs(z.real),np.abs(z.imag))
                    z = z**2 + c
                    #z = z**-z + ( z / ( c + complex(0.001,0.001) ) )
                else:
                    pass

                    #z = z**z + ( a / c ) * (np.cos(temp/c)*np.sin(temp/c))
                    #c = (c**c) + (z**3) / np.tan(z*c)
                    #z = z**(z/1.5) - np.cos(c) + (z**3)
                    #z = z**2 + np.tan(c)

                    #m = (c/(2*z))
                    #z = z**2 - (c*np.arctan(m.real+m.imag))

                    z = z**z + ( z / ( c + complex(0.001,0.001) ) )

                    #z = ( z / np.cos( z - c )**( z / ( c + complex(0.001,0.001) ) + c))
                if(str(z)=="(nan+nanj)"):
                    #print("YES")
                    return [pixel,[(scaleToRangeSimple(i,[0,l],[0,360],colorExponent)),i]]
                
            except Exception:
                #return ( mapRange( (pixel[0]/(pixel[1]+1))*i, [0,(frame[0]/frame[1])*l], [0,360] ) )
                return [pixel,[(scaleToRangeSimple(i,[0,l],[0,360],colorExponent)),i]]
    return [pixel,[-1,256]]
    #return -1"""

if __name__=="__main__":

    start = datetime.datetime.now()
    now = start

    print("\nStarted {"+str(frame[0])+"px X "+str(frame[1]) +"px} at: "+getTime()+" with "+str(l)+" i/px","\n")
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
        if((i/(frame[0]*frame[1]) * 100)%int(100/consoleReadouts) == 0):
            now = datetime.datetime.now()
            print(str(int((i/(frame[0]*frame[1])) * 100))+"%","@ "+getTime(),"("+str(i)+"/"+str(frame[0]*frame[1])+")")
        if(e[1][0]==-1): data[(e[0][0],e[0][1])] = (0,0,0)
        else: data[(e[0][0],e[0][1])] = (int(((e[1][0]*cScale)+cOffset)%360), 256, lightnessScale*int((e[1][1])**lightnessExponent))

    now = datetime.datetime.now() 
    print("\nSAVING IMAGE\n@"+getTime())

    scale = 1
    if(scaling or (frame[0]<1920) or (frame[1]<1920)): 
        scale = 1920//frame[0] if frame[0]<1920 else 1920//frame[1]
    img.convert( mode="RGB" ).resize((frame[0]*scale,frame[1]*scale),0).save( location+name+"_"+str(1)+'.png' )

    now = datetime.datetime.now()
    d = now - start
    print("\nFinished {"+str(frame[0])+"px X "+str(frame[1]) +"px} in "+str(d.total_seconds())+" Seconds!")
