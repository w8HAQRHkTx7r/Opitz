import csv
import getopt
import sys
import math
import simplekml
from collections import namedtuple
import time

# Set defaults
# (default flag, value)
starttime = time.time()
Option = namedtuple('Option', 'default value')
KMLDESCRIPTION = Option(True, 'GENERIC')
CSVNAME =        Option(True, 'generic.csv')
MODULUS =        Option(True, 0)
KMLNAME =        Option(True, 'generic.kml')
PCTREDUCTION =   Option(True, 0.50)
ALTSCALING =     Option(True, 1.0)
EPSILON =        Option(True, 0.0)
MAXPOINTS =      Option(True, 0)
EXTRUDE =        Option(True, False)
CALLOUT =        Option(True, False)
FEETPERDEGREE =  288000.0
FEET =           0.0

def printUsage():
    print('RDP -i <file> -o <file> [-d <desc>] [-s <scale>] [-e epsilon | [[-m <mod>] [-r <pct>][-p count]]] -x [-h]')
    print('   i   Input .csv file name')
    print('   o   Output .kml file name')
    print('   d   KML descriptive name')
    print('   s   Altitude scaling factor')
    print('   x   extrude')
    print(' Reduction parameters:')
    print('   e   Epsilon in feet')
    print('   -- or')
    print('   m   Take every mth observation')
    print('   r   Target percent reduction')
    print('   p   Point limit')
    print('   c   Include POI callouts')
    
parameters = sys.argv[1:]
try:
   opts, args = getopt.getopt(parameters,"d:i:m:o:r:s:e:p:xch")
except getopt.GetoptError:
   print("Oops! Can't get parameters")
   printUsage()
   sys.exit(2)

for opt, arg in opts:
   if opt == '-d':
      KMLDESCRIPTION = KMLDESCRIPTION._replace(default = False, value = arg)
   elif opt in ('-i'):
      CSVNAME = CSVNAME._replace(default = False, value = arg)
   elif opt in ('-m'):
      MODULUS = MODULUS._replace(default = False, value = int(arg))
   elif opt in ('-o'):
      KMLNAME = KMLNAME._replace(default = False, value = arg)
   elif opt in ('-r'):
      PCTREDUCTION = PCTREDUCTION._replace(default = False, value = float(arg))   
   elif opt in ('-s'):
      ALTSCALING = ALTSCALING._replace(default = False, value = float(arg))
   elif opt in ('-e'):
      FEET = float(arg)
      EPSILON = EPSILON._replace(default = False, value = float(FEET)/FEETPERDEGREE)
   elif opt in ('-p'):
      MAXPOINTS = MAXPOINTS._replace(default = False, value = int(arg))
   elif opt in ('-x'):
      EXTRUDE = EXTRUDE._replace(default = False, value = True)
   elif opt in ('-c'):
      CALLOUT = CALLOUT._replace(default = False, value = True)
   elif opt == '-h':
      printUsage()
      sys.exit(1)
   else:
      printUsage()
      sys.exit(1)
      
print("Program parameters")
print(f'  KML description:       {KMLDESCRIPTION.value}')
print(f'  Input file name:       {CSVNAME.value}')
print(f'  Output file name:      {KMLNAME.value}')
print(f'  Altitude scale factor: {ALTSCALING.value}')
print(f'  Extrude:               {EXTRUDE.value}')
print(f'** Reduction criteria')
print(f'  Modulus:               {MODULUS.value}')
print(f'  epsilon:               {EPSILON.value}')
print(f'  Max points limit:      {MAXPOINTS.value}')
print(f'  % reduction:           {PCTREDUCTION.value}')
print(f'\n')

# Read the .csv input
# Parse it into lon, lat and alts
# Adjust alt by the minimum observed
# and scale it

timestamp = []
lon       = []
lat       = []
alt       = []

with open(CSVNAME[1], newline='') as fh: # Open our file.
    csv_reader = csv.reader(fh) # Create our reader object.
    next(csv_reader,None)
    for row in csv_reader: # Iterate over each row.
#        print(row) # Print entire row
#        print(row[1], row[2], row[3]) # Print only certain columns
#        timestamp.append(row[0])
#        lat.append(float(row[1]))
#        lon.append(float(row[2]))
#        alt.append(float(row[3]))
#        timestamp.append(row[0])
        lon.append(float(row[0]))
        lat.append(float(row[1]))
        alt.append(float(row[2]))

print(f'Total points: {len(lat)}')

zero = min(alt) - 1.0
print(f'lowest altitude: {zero + 1.0}')

scaled = [(a - zero) * ALTSCALING.value for a in alt]
for i in range(0,len(scaled)):
#	print(f'{alt[i]:.6} {scaled[i]:.6}')
	continue
		
def computeLine(p1, p2):
#	print(f'p1: {p1} p2: {p2}')
	standardform = dict(A=0.0, B= 0.0, C = 0.0, slopeintercept= "y=mx+b")
	p1y, p1x = p1
	p2y, p2x = p2
	standardform["A"] = p2y - p1y
	standardform["B"] = p2x - p1x
	standardform["C"] = p2x * p1y - p2y * p1x
#	print(standardform)
	if p2x == p1x:
		m = 0.0
	else:
		m = (p2y - p1y) / (p2x - p1x)
	b = p2y - (m * p2x)
	standardform["slopeintercept"] = f'y={m}x+{b}'
	return standardform

p1 = (lat[0],lon[0])
p2 = (lat[len(lat)-1],lon[len(lon)-1])
sf = computeLine(p1,p2)
p1f = '({:.7} {:.7})'.format(*p1)
p2f = '({:.7} {:.7})'.format(*p2)
print(f'Line from {p1f} to {p2f} is {sf["slopeintercept"]}')

def perpendicularDistanceFromLine(sf, point):
	y,x = point
	D = abs(sf["A"]*x-sf["B"]*y+sf["C"]) / math.sqrt(sf["A"] ** 2 + sf["B"] ** 2)
#	print(f'{D}=|{sf["A"]}*{x}-{sf["B"]}*{y}+{sf["C"]}| / root({sf["A"]} ** 2 + {sf["B"]} ** 2)')
	return D	

maxdistance = -1.0
savedIndex = 0
for i in range(0,len(lon)):
	testpoint = (lat[i],lon[i])
	distanceToLine = perpendicularDistanceFromLine(sf, testpoint)
#	print(f'{i}: distance from {testpoint} to line: {distanceToLine} feet {288200 * distanceToLine}')
	if distanceToLine > maxdistance:
		maxdistance = distanceToLine
		savedIndex = i
#		print(f'{savedIndex} {lon[i]} {lat[i]}')
print(f'Furthest point is {savedIndex} {lat[savedIndex]:12.7}, {lon[savedIndex]:12.7} -- {maxdistance:.7} {FEETPERDEGREE * maxdistance:.7} feet')

def writeKeptPoints(filename, ts,la,lo,al):
	# open the file in the write mode
	f = open(filename, 'w')
	writer = csv.writer(f)
	for i in range(0, len(keptPoints)):
		row = timestamp[i], lat[i], lon[i], alt[i] # write a row to the csv file
		writer.writerow(row)
	f.close()

def turnDataIntoKML(keptPoints):
	coords = keptPoints
	kml = simplekml.Kml()
	linestring = kml.newlinestring(name=KMLDESCRIPTION.value)
	linestring.coords = coords
	linestring.altitudemode = simplekml.AltitudeMode.relativetoground
	linestring.style.linestyle.color = simplekml.Color.yellow
	linestring.style.polystyle.color = simplekml.Color.yellow
	if EXTRUDE.value:
		linestring.extrude = 1
	if CALLOUT.value:
		print(f'\nPoints of Interest\n')
		poilon = (
		-73.99268,	-75.13012,	-76.32318,	-77.21174,	-77.09699,	-77.175026,	-78.0975,	-78.38106,	-78.67188,	-79.13541,			-79.60444,	-79.94975,	-80.3208,	-80.72614,	-81.15652,	-81.41558,	-81.73954,	-82.22116,	-82.571434,	-82.407394,	-83.40391,	-83.740105,	-84.55074,	-85.344124,	-85.3045,	-85.67347,	-86.39702,	-87.286804,	-87.891556,	-88.18037,	-88.709114,	-89.321846,	-89.328674,	-89.62148,	-88.29695,	-88.721146,	-89.7833,	-90.98149,	-91.963974,	-92.72624,	-92.42877,	-91.80944,	-91.67961,	-91.4643,	-91.62691,	-90.704834,	-90.333954,	-90.17158,	-89.552315,	-89.10062,	-88.824066,	-87.98293,	-87.81022,	-87.577576,	-88.09404,	-87.794716,	-87.6467,	-86.34438,	-85.149216,-83.59223,	-82.20943,	-80.81936,	-79.94172,	-79.49503,	-79.08133,	-78.635414,	-78.50206,	-77.92671,	-76.7991,	-75.7535,	-74.76934,	-73.9719,	-73.9932
		)
		poilat = (
	40.745346,	40.35138,	40.042835,	39.83718,	38.965622,	38.81523,	38.76515,	38.594814,	38.246613,	37.852364,	37.448296,	37.270203,	36.83932,	36.641212,	36.429573,	36.28078,	36.139626,	35.75169,	35.69548,	34.85637,	34.867283,	34.391384,	34.00981,	34.434692,	35.03573,	35.180367,	35.815186,	36.09844,	36.479057,	36.946426,	37.146408,	37.660896,	38.65481,	39.8568,	40.078056,	40.4171,	40.800125,	40.851543,	40.9925,	41.701134,	42.553802,	43.299583,	44.076164,	44.779663,	45.32774,	45.22017,	45.135498,	44.642147,	44.502956,	44.369465,	43.50373,	42.992535,	42.43017,	41.77096,	41.965935,	41.890736,	41.860813,	41.54581,	41.297253,	41.309116,	41.125443,	40.902428,	40.46166,	39.882645,	40.01905,	40.026398,	40.017082,	40.000137,	40.21475,	40.766502,	41.02433,	41.367973,	40.74556	)


		poilabels = ['START/FINISH', 'Danboro, PA', 'Lancaster, PA', 'Gettysburg, PA', 'Bathesda, MD', 'Alexandria, VA',
	'Flint Hill, VA', 'Skyland Lodge', 'Loft Mnt. Campground', 'Montebello Camping and Fishing Resort',
	'Peaks of Otter Lodge', 'Roanoke, VA', 'Floyd, VA', 'Fancy Gap, VA', 'Doughton Park Campground, VA',
	'West Jefferson, NC', 'Blowing Rock, NC', 'Black Mountain Campground', 'Weaverville, NC',
	'Greenville, NC', 'Clayton, GA', 'Don Carter State Park', 'Marietta, GA', 'Summerville, GA', 'Chattanooga, TN',
	'Sequatchie, TN', 'Murfreesboro, TN', 'Burns, TN', 'Dover, TN', 'Hillman Ferry Campground', 'Metropolis, IL',
	'Carbondale, IL', 'Carlyle, IL', 'Springfield, IL', 'Champaign, IL', 'Le Roy, IL', 'Brimfield, IL',
	'Gladstone, IL', 'Fairfield, IA', 'Grinnell, IA', 'Cedar Falls, IL', 'Decorah, IA', 'Winona, MN',
	'Eau Claire, WI', 'Chetek, WI', 'SPLIT', 'Medford, WI', 'Marshfield, WI', 'Stevens Point, WI', 'Waupaca, WI', 
	'Beaver Dam, WI', 'Milwaukee, WI', 'Zion, IL', 'Chicago, IL', '', 'Roselle, IL', 'Oak Park, IL', 'Chicago, IL',
	'North Liberty, IN', 'Garrett, IN', 'Portage, OH', 'Wellington, OH', 'Salem, OH', 'Pittsburgh, PA',
	'Ohiopyle, PA', 'Somerset, PA', 'Schellsburg, PA', 'Bedford, PA', 'McConnelsburgh, PA',
	'Harrisburg, PA', 'Lehighton, PA', 'Newton, NJ', 'Highland Falls, NY'
	
	'']

		poi = list(zip(poilon,poilat))

		for i in range(0, len(poilabels)):
#			print(i, poilabels[i], poi[i])
			pnt = kml.newpoint()
			pnt.name = f'{poilabels[i]}'
			pnt.style.labelstyle.color = simplekml.Color.yellow
			pnt.style.labelstyle.scale = 0.7
			pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
			pnt.coords = [poi[i]]
			pnt = None

		pnt = kml.newpoint()

		pnt.name = 'Elkhart Hill Overpass'
		pnt.style.labelstyle.color = simplekml.Color.red
		pnt.style.labelstyle.scale = 1
		pnt.style.balloonstyle.text = 'This is the legenary overpass'
		pnt.style.balloonstyle.textcolor = simplekml.Color.rgb(0, 0, 255)
		pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
		pnt.coords = [(-89.4711669,40.0203009)]

	kml.save(KMLNAME.value)

keptPoints = []
if MODULUS.value != 0:
	print(f'\n\n============================')
	print(f'Modulo {MODULUS[1]}')
	print(f'============================')
	for i in range(0,len(lon), MODULUS.value):
	#	print(f'{i}')
		keptPoints.append((lon[i], lat[i], scaled[i]))
	
	print(f'\nThere are {len(keptPoints)} points kept\n')
	desc = f'MOD {MODULUS.value} # {len(keptPoints)}'
	KMLDESCRIPTION = Option(False, desc)
	if KMLNAME.default:
		KMLNAME = Option(False, f'MOD{MODULUS.value}.kml')
	turnDataIntoKML(keptPoints)
	writeKeptPoints('MODKept.csv', timestamp, lat, lon, scaled)

def RamerDouglasPeuker(lat, lon, startIndex, endIndex, e):

	assert startIndex < endIndex

	if startIndex >= endIndex:
		print(f'Fatal error!  startIndex ({startIndex}) is >= endIndex ({endIndex})')
		print(f'Returning an empty list')
		return []

	if len(lat) <= 2:
		return [startIndex, endIndex]

	# There are only two points.  Just return them.
	if startIndex + 1 == endIndex:
		return [startIndex, endIndex]

	p1 = (lat[startIndex],lon[startIndex])
	p2 = (lat[endIndex],lon[endIndex])
	sf = computeLine(p1,p2)

	maxdistance = -1.0
	savedIndex = 0
	for i in range(startIndex,endIndex):
		testpoint = (lat[i],lon[i])
		distanceToLine = perpendicularDistanceFromLine(sf, testpoint)
		if distanceToLine > maxdistance:
			maxdistance = distanceToLine
			savedIndex = i
	
	indexArray = []
	if maxdistance > e:
		leftResults =  RamerDouglasPeuker(lat, lon, startIndex, savedIndex, e)
		rightResults = RamerDouglasPeuker(lat, lon, savedIndex, endIndex,   e)
		indexArray.extend(leftResults)
		rightResults.pop(0)
		indexArray.extend(rightResults)
	else:
#		print(f'   No points are outside of epsilon')
		indexArray.append(startIndex)
		indexArray.append(endIndex)
	return indexArray


keptPoints = []
if EPSILON.value != 0.0:
	print(f'\n\n============================')
	print(f'Ramer-Deimer-Peuker')
	print(f'============================')
	print(f'error = {FEET} ft.')
	print(f'epsilon = {EPSILON.value}')

	keptIndices = RamerDouglasPeuker(lat, lon, 0, len(lon)-1, EPSILON.value)
	print(f'RDP retained {len(keptIndices)} points @ epsilon {EPSILON.value}')

	for i in range(0,len(keptIndices)):
		keptPoints.append((lon[keptIndices[i]], lat[keptIndices[i]], scaled[keptIndices[i]]))
#		print(f'alt: {alt[keptIndices[i]]} scaled: {scaled[keptIndices[i]]}')
	
	if KMLNAME.default:
		newname = 'RDP' + KMLNAME.value
		KMLNAME = KMLNAME._replace(value = newname)
	
	desc = f'e {FEET} ({EPSILON.value:.6}) # {len(keptPoints)}'
	KMLDESCRIPTION = Option(False, desc)
	turnDataIntoKML(keptPoints)
#	writeKeptPoints('RDPKept.csv', timestamp, lat, lon, scaled)


elapsed = time.time() - starttime
print(f"Elapsed time: {elapsed}") 
