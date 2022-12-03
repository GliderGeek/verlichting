"""
This script take one commandline argument: filepath of gpx
It outputs two files for using in trips db:
- track.json
- stops.json
"""

import json
from xml.dom import minidom
import sys

# parse an xml file by name
filename = sys.argv[1]
file = minidom.parse(filename)

#use getElementsByTagName() to get tag
trksegs = file.getElementsByTagName('gpx')[0].getElementsByTagName('trk')[0].getElementsByTagName('trkseg')


track = []
i = 0
segment_indices = []

for trkseg in trksegs:
	segment_indices.append(i)
	for pnt in trkseg.getElementsByTagName('trkpt'):
		lon = float(pnt.attributes['lon'].value)
		lat = float(pnt.attributes['lat'].value)
		track.append([lon, lat])
		i += 1

print(segment_indices, len(segment_indices))
print(len(track), track[0])

with open('track.json', 'w') as f:
	json.dump(track, f)

stops = []
for i, index in enumerate(segment_indices):
	stops.append({'index': index, 'name': 'stop%s' % i})
with open('stops.json', 'w') as f:
	json.dump(stops, f)
