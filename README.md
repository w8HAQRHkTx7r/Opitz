# Opitz
RideWithGPS is a program to plan and track bicycle rides.
To track a ride, you launch the app on your phone and hit the record
button.  Every 2 seconds(?) it records a GPS lon/lat.  When the 
ride is completed, the app pushes all the data up to the web.
You can export the ride from the web as a .kml file.  The contents looks
like:

```
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document id="1">
        <Style id="4">
            <LineStyle id="5">
                <color>ff00ffff</color>
                <colorMode>normal</colorMode>
            </LineStyle>
            <PolyStyle id="6">
                <color>ff00ffff</color>
                <colorMode>normal</colorMode>
                <fill>1</fill>
                <outline>1</outline>
            </PolyStyle>
        </Style>
        <Placemark id="3">
            <name>e 24.0 (8.33333e-05) # 480</name>
            <styleUrl>#4</styleUrl>
            <LineString id="2">
                <extrude>1</extrude>
                <altitudeMode>relativeToGround</altitudeMode>
                <coordinates>
-85.221582,39.853677,353.4
-85.227315,39.853566,340.6
...
```

I manually edit this file tossing away everything except the coordinates values.  

Then I run that file through my rdp.py program.  I wrote rdp.py to create a kml
file from lon,lat,alt values.

To get a list of the program's command line parameters, run 

     python3 rdp.py -h

Here's my typical typical usage:

     python3 rdp.py -i all_points.csv -o reduced_points.kml -e 24 -s 5 -x

- all_points.csv are the coordinates from the exported bike ride with all the
xml tags removed.  THERE IS NO HEADER IN THIS FILE.

- reduced_points.kml will be the route with fewer points

- 24 is the error or tolerence.  24 feet is the width of a two-lane country road.  The larger
the number, the fewer points, but the less accurate the path.

- 5 is the scaling factor for altitude.

- x specifies that the kml should have an extrusion.

This creates a great looking Google Earth Map.

Here's the console output:

👉 python3 rdp.py -i all_points.csv -o reduced_points.kml -e 24 -s 5 -x 
Program parameters
  KML description:       GENERIC
  Input file name:       all_points.csv
  Output file name:      reduced_points.kml
  Altitude scale factor: 5.0
  Extrude:               True
** Reduction criteria
  Modulus:               0
  epsilon:               8.333333333333333e-05
  Max points limit:      0
  % reduction:           0.5


Total points: 10730
lowest altitude: 109.3
Line from (43.38507 -72.63364) to (43.38507 -72.63371) is y=-0.0x+43.38507
Furthest point is 2939     43.99332,    -72.43054 -- 0.60825 175176.0 feet


============================
Ramer-Deimer-Peuker
============================
error = 24.0 ft.
epsilon = 8.333333333333333e-05
RDP retained 1569 points @ epsilon 8.333333333333333e-05
Elapsed time: 0.0816192626953125

The original path had 10730 track points.  This was reduced to 1569.
I then took this 1569 point kml, cut and pasted the <coordinates> into a .csv file,
added a lat,lon,alt header and ran that through your csv_to_stl.py program. I brought
that .stl output into TinkerCAD.

