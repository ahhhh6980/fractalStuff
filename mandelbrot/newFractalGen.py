import numpy as np
import multiprocessing
from PIL import Image, ImageOps
from PIL.PngImagePlugin import PngImageFile, PngInfo
import datetime
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

# Functions
def log( b, x ): 
    try: return( np.log(x) / np.log(b) )
    except Exception:
        return 0

# Map i from range a to range b
def mapRange( i, a, b ): return (( i - a[0] ) / a[1]) * (b[1] - b[0]) + b[0]
# Above but more complex, outputs exponentially to value e
def scaleToRangeSimple( i, a, b, e ):
    return ( np.power(  i - a[0], ( e + log(i - a[0], b[1] - b[0]) )  ) / np.power(a[1] - a[0], e) + b[0] )

def getTime(): return ( "{" + str(now.hour) + "h:" + str(now.minute) + "m:" + str(now.second) + "." + str(now.microsecond) + "s}" )

# for pre-generating
def split( sV, i ): 
    q = i%sV,i//sV
    cX = [ int(np.ceil(mapRange( q[0], [0,sV], [0,frame[0]] ))), int(np.ceil(mapRange( q[0]+1, [0,sV], [0,frame[0]] ))) ]
    cY = [ int(np.ceil(mapRange( q[1], [0,sV], [0,frame[1]] ))), int(np.ceil(mapRange( q[1]+1, [0,sV], [0,frame[1]] ))) ]
    return [ [x,y] for x in range(*cX) for y in range(*cY) ]

def splitINFO( sV, i ): 
    q = i%sV,i//sV
    cX = [ str(int(np.ceil(mapRange( q[0], [0,sV], [0,frame[0]] )))), str(int(np.ceil(mapRange( q[0]+1, [0,sV], [0,frame[0]] )))) ]
    cY = [ str(int(np.ceil(mapRange( q[1], [0,sV], [0,frame[1]] )))), str(int(np.ceil(mapRange( q[1]+1, [0,sV], [0,frame[1]] )))) ]
    return "X Range: (" + cX[0] +":"+ cX[1] + "), Y Range: (" + cY[0] +":"+ cY[1]+")"

def writeMetaData():
    m = PngInfo()
    m.add_text( "Creator:", config.get('fileNaming', 'creatorTag') )
    return m

def cotanh(n): return np.cosh(n)/np.sinh(n)

# Config.get('section', 'option')
# Config.getboolean('section', 'option')

availableCores = multiprocessing.cpu_count() - int(config.get('misc', 'threadExclude'))
posX = float(config.get('misc', 'posX'))
posY = float(config.get('misc', 'posY'))
position = complex( posX, posY )

theta = int(config.get('misc', 'angle'))
angle = (theta * np.pi) / 180

px = float(config.get('misc', 'anglePosX'))
py = float(config.get('misc', 'anglePosY'))
p = complex( px, py )
if(theta!=0): position += complex( p.real * np.cos(angle) + p.imag * np.sin(angle), (p.real) * np.sin(-angle) + p.imag * np.cos(angle) )

zoom = float(config.get('misc', 'zoom'))

resolution = float(config.get('main', 'resolution'))
rX = float(config.get('main', 'ratioX'))
rY = float(config.get('main', 'ratioY'))
ratio = [ rX, rY]

imageDiv = int(config.get('main', 'imageDiv'))
fancyColors = config.getboolean('colors', 'fancyColors')
cScale = float(config.get('colors', 'cScale'))
cOffset = 45 * int(config.get('colors', 'cOffset'))
colorExponent = float(config.get('colors', 'colorExponent')) 
lightnessExponent = float(config.get('colors', 'lightnessExponent'))
lightnessScale = int(config.get('colors', 'lightnessScale'))

l = int(config.get('misc', 'limit'))

isMandelbrot = config.getboolean('main', 'isMandelbrot')
isBurningShip = config.getboolean('main', 'isBurningShip')
isJulia = config.getboolean('main', 'isJulia')
juliaX = float(config.get('misc', 'juliaCoordX'))
juliaY = float(config.get('misc', 'juliaCoordY'))
juliaCoord = complex( juliaX, juliaY )

loadDefaults = config.getboolean('main', 'loadDefaults')

if(isMandelbrot and loadDefaults):
    cScale = 0.5
    lightnessExponent = 1.5
    colorExponent = 0.4
    l = 2500
    zoom = 0.7
    ratio = [ 4, 3.5 ]
    position = complex( -0.25, 0.5 )

if(isBurningShip and loadDefaults):
    cScale = 0.75
    cOffset = 90
    lightnessExponent = 2.0
    lightnessScale = 2
    colorExponent = 0.4
    zoom = 55
    ratio = [ 3, 6 ]
    position = complex( -1.124, 0.4685 )

if(isJulia and loadDefaults):
    zoom = 0.7
    position = complex( 0.5, 0.5 )
    l = 2500
    colorExponent = 0.15 * (cScale/2)
    ratio = [ 3, 3 ]

frame = [ round( 60 * ratio[0] * resolution ), round( 60 * ratio[1] * resolution ) ]
img = Image.new( 'HSV', [ frame[0], frame[1] ], ( 100, 0, 360 ) )
data = img.load()

informativeName = config.getboolean('fileNaming', 'informativeName')
location = config.get('fileNaming', 'location')
number = config.get('fileNaming', 'number')
juliaString = "j(" + str(juliaCoord.real) + ", "+str(juliaCoord.imag) + ")"
posString = "p(" + str(position.real) + ", " + str(position.imag) + ")"
if( informativeName ):
    name = "#" + str(number)
    if(isJulia): name += juliaString
    name += posString + " " + str(l) + "l s[" + str(frame[0]) + "," + str(frame[1]) + "] " + " z"+str(zoom)
    if( theta != 0 ): name += " rot" + str(theta)
else: name = "#"+str(number)

consoleReadouts = int(config.get('misc', 'consoleReadouts'))
scaling = config.getboolean('main', 'scaling')
exclude = config.getboolean('misc', 'exclude')
scale = 1

# Computation function
def computePixel( pixel ):
    c = (complex( mapRange( pixel[0] , [0,frame[0]], [-1,1] )/zoom, (frame[1]/frame[0]) * mapRange( pixel[1] , [0,frame[1]], [-1,1] )/zoom ))
    if(theta!=0):
        c = complex( c.real * np.cos(angle) + c.imag * np.sin(angle), (-c.real) * np.sin(angle) + c.imag*np.cos(angle) ) - ( complex( 0.5, 0.5 ) - position )
    else: c -= ( complex( 0.5, 0.5 ) - position )
    z = c
    p = np.sqrt( ( c.real - 0.25 ) ** 2 + c.imag ** 2 )
    # Exclude cardioid and main bulb
    temp = 12
    d = float("1e20")
    if( isJulia ): c = juliaCoord
    if( isJulia or ( isMandelbrot == False ) or ( exclude or (isMandelbrot and (( c.real > p - ( 2 * p**2 ) + 0.25 and ( c.real + 1 ) ** 2 + ( c.imag**2 ) > 1/16 ))) )):
        for i in range(l):
            try:
                if(isMandelbrot and not(isBurningShip)):

                    z = z**2 + c

                elif( isBurningShip and not(isMandelbrot) ):

                    z = complex( np.abs(z.real), np.abs(z.imag) )
                    z = z**2 + c

                else:
                    pass
                # commented sections are other formulas

                    #z = z**z + ( a / c ) * (np.cos(temp/c)*np.sin(temp/c))

                    #c = (c**c) + (z**3) / np.tan(z*c)
                    #z = z**(z/1.5) - np.cos(c) + (z**3)

                    #z = z**2 + np.tan(c)

                    #m = (c/(2*z))
                    #z = z**2 - (c*np.arctan(m.real+m.imag))

                    z = z**z + ( z / ( c + complex(0.001,0.001) ) ) 
                
                if( str(z) == "(nan+nanj)" ):
                    #print("YES")
                    if(fancyColors):
                        return [ pixel, [ ( scaleToRangeSimple( i, [0,l], [0,360], colorExponent*d ) ), i, d ] ]
                    else: return [ pixel, [ ( scaleToRangeSimple( i, [0,l], [0,360], colorExponent ) ), i ] ]
            except Exception:
                #return ( mapRange( (pixel[0]/(pixel[1]+1))*i, [0,(frame[0]/frame[1])*l], [0,360] ) )
                if(fancyColors):
                    return [ pixel, [ ( scaleToRangeSimple( i, [0,l], [0,360], colorExponent*d ) ), i, d ] ]
                else: return [ pixel, [ ( scaleToRangeSimple( i, [0,l], [0,360], colorExponent ) ), i ] ]
            if(fancyColors):
                try: 
                    d = min( np.abs(z-c) , d)
                except: pass
    return [ pixel, [-1,256, d] ]
    #return -1"""

if __name__=="__main__":

    #START
    start = datetime.datetime.now()
    now = start
    print( "\nStarted {" + str(frame[0]) + "px X " + str(frame[1]) + "px}\n@ " + getTime() + " with " + str(l) + " i/px" )
    
    
    for segment in range(2**imageDiv):
        startSegment = datetime.datetime.now()
        #MULTIPROCESS
        now = datetime.datetime.now() - start
        print( "\nPROCESSING SEGMENT "+str(segment)+" {"+str(int(frame[0]/imageDiv))+"px X "+str(int(frame[1]/imageDiv))+"px}\n>>Current Runtime: " + str(now.total_seconds()) + "s"+"\n"+splitINFO( imageDiv, segment ) )

        p = multiprocessing.Pool(availableCores)
        r = p.map( computePixel, split( imageDiv, segment ) )
        p.close()
        p.join()

        #COLOR ASSIGN
        i = 0
        now = datetime.datetime.now() - start
        print( "\nSTARTING COLOR ASSIGNMENT OF S"+str(segment)+"\n>>Current Runtime: " + str(now.total_seconds()) + "s" )

        for e in r:

            i+=1
            if( ( i / ( frame[0]/imageDiv * frame[1]/imageDiv ) * 100 ) % int( 100 / consoleReadouts ) == 0 ):
                now = datetime.datetime.now() - start
                print( str( int( (i / ( frame[0]/imageDiv * frame[1]/imageDiv ) ) * 100) ) + "%", "<Current Runtime: " + str(now.total_seconds()) + "s>", "(" + str(i) + "/" + str( int(frame[0]/imageDiv * frame[1]/imageDiv) ) + ")" )
            
            # Fancy (and trippy), but slower colors
            if(fancyColors):

                try:
                    if(e[1][0]==-1): 
                        data[ (e[0][0], e[0][1]) ] = ( 0, 0, 0 )
                    else: 
                        data[ (e[0][0], e[0][1]) ] = (int( ( e[1][0] * cScale * (2-e[1][2]) ) + cOffset ) % 360 , 256,  int( int( (e[1][1]) ** lightnessExponent )))
                except: data[ (e[0][0], e[0][1]) ] = ( 0, 0, 0 )
            
            # Normal, faster colors
            else:

                if(e[1][0]==-1): 
                    data[ (e[0][0], e[0][1]) ] = ( 0, 0, 0 )
                else: 
                    data[ (e[0][0], e[0][1]) ] = (int( ( e[1][0] * cScale ) + cOffset ) % 360 , 256, lightnessScale * int( e[1][1] ** lightnessExponent ))
        
        now = datetime.datetime.now()
        d = now - startSegment
        print( "\Segment "+str(segment)+" done in [" + str(d.total_seconds()) + " Seconds]" )
    
    #SAVING
    now = datetime.datetime.now() - start
    print( "\nSAVING IMAGE\n>>Current Runtime: " + str(now.total_seconds()) + "s" )

    metadata = writeMetaData()
    if( scaling or frame[0] < 1920 or frame[1] < 1920 ): 
        scale = 1920//frame[0] if frame[0] < 1920 else 1920 // frame[1]
    
    try:
        img.convert( mode = "RGB" ).resize( (  frame[0] * scale, frame[1] * scale  ), 0 ).save( location + name + '.png', pnginfo = metadata )
    except FileNotFoundError:
        print("Images folder not found, saving to current working directory")
        img.convert( mode = "RGB" ).resize( (  frame[0] * scale, frame[1] * scale  ), 0 ).save( name + '.png', pnginfo = metadata )
    
    now = datetime.datetime.now()
    d =  now - start
    print( "\nFinished {" + str(frame[0]) + "px X " + str(frame[1]) + "px} in " + str(d.total_seconds()) + " Seconds!" +  "\n@ " + getTime() )
