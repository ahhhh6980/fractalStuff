import numpy as np
import multiprocessing
from PIL import Image, ImageOps
from PIL.PngImagePlugin import PngImageFile, PngInfo
import datetime

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
    m.add_text( "Creator:", "Ahhhh#6980" )
    return m

availableCores = multiprocessing.cpu_count()
# Setup
# Coordinate on fractal image will be centered on
position = complex( 1.45, 0.5 )
# If you want to angle the fractal
# Slightly slower rendering if value is not zero
# p offsets vertically and horizontally independant of rotation :)
theta = 0
angle = (theta * np.pi) / 180
p = complex( -1, 0.35 )
if(theta!=0):
    position += complex( p.real * np.cos(angle) + p.imag * np.sin(angle), (p.real) * np.sin(-angle) + p.imag * np.cos(angle) )

zoom = 0.5

# Be careful, high resolutions take a LOT of ram
# For 16:9, 5 gives you a 4800px X 2700px image, which may require up to or over 8gb of ram
# resolution * 60 * ratio = image size
resolution = 0.5
ratio = [ 24, 18]

# will split into 2**imageDiv chunks
# more chunks = slightly slower, only use for large images if your pc struggles to keep pre-processed data in memory
# seems to only work with even numbers ¯\_(ツ)_/¯
# For images smaller than 1920x1080, keep this at or below 4 (16 chunks)
imageDiv = 2

# Fancy (and trippy), but slower colors
fancyColors = True

# slight color adjustment
cScale = 0.75
cOffset = 45 * 2
colorExponent = 0.05
lightnessExponent = 2
lightnessScale = 2

# iteration limit
l=2500

# These can override settings
isMandelbrot = False
isBurningShip = False
isJulia = False
juliaCoord = complex( 0.2, -0.7 )

if(isMandelbrot):
    l = 2500
    zoom = 0.7
    ratio = [ 4, 3.5 ]
    position = complex( -0.25, 0.5 )

if(isBurningShip):
    colorExponent = 0.4
    zoom = 0.5
    #zoom = 55
    #ratio = [ 3, 6 ]
    ratio = [4,4]
    #position = complex( -1.124, 0.4685 )
    position = complex( 0, 0.5 )

if(isJulia):
    zoom = 0.7
    position = complex( 0.5, 0.5 )
    l = 2500
    colorExponent = 0.15 * (cScale/2)
    colorExponent = 0.1
    ratio = [ 3, 3 ]

# Frame setting and image setup
frame = [ round( 60 * ratio[0] * resolution ), round( 60 * ratio[1] * resolution ) ]
img = Image.new( 'HSV', [ frame[0], frame[1] ], ( 100, 0, 360 ) )
data = img.load()

# Saving Info
informativeName = False
location = ''
number = 7
juliaString = "j(" + str(juliaCoord.real) + ", "+str(juliaCoord.imag) + ")"
posString = "p(" + str(position.real) + ", " + str(position.imag) + ")"
if( informativeName ):
    name = "#" + str(number) + juliaString + posString + " " + str(l) + "l s[" + str(frame[0]) + "," + str(frame[1]) + "] " + " z"+str(zoom)
    if( theta != 0 ): name += " rot" + str(theta)
else: name = "#"+str(number)

consoleReadouts = 5
scaling = False

exclude = True

def cotanh(n):
    return np.cosh(n)/np.sinh(n)

# Computation function
def computePixel( pixel ):
    c = (complex( mapRange( pixel[0] , [0,frame[0]], [-1,1] )/zoom, (frame[1]/frame[0]) * mapRange( pixel[1] , [0,frame[1]], [-1,1] )/zoom ))
    if(theta!=0):
        c = complex( c.real * np.cos(angle) + c.imag * np.sin(angle), (-c.real) * np.sin(angle) + c.imag*np.cos(angle) ) - ( complex( 0.5, 0.5 ) - position )
    else: c -= ( complex( 0.5, 0.5 ) - position )
    z = c
    z2 = z
    c2 = c
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
                    #z = z**z + ( z / (c + complex(0.001,0.001)) ) + np.sin(np.sinh(z)/cotanh(z2))/np.sin(cotanh(c2)/np.sinh(c))
                
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
    scale = 1
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
