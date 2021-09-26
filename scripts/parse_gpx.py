import json
from xml.dom import minidom

# parse an xml file by name
file = minidom.parse('Frankr21.gpx')

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




# trkpts = trksegs[0].getElementsByTagName('trkpt')
# print('lon:', float(trkpts[0].attributes['lon'].value))



# for segment in trksegs

# print(len(trksegs))



# print(models)

# # one specific item attribute
# print('model #2 attribute:')
# print(models[1].attributes['name'].value)

# # all item attributes
# print('\nAll attributes:')
# for elem in models:
#   print(elem.attributes['name'].value)

# # one specific item's data
# print('\nmodel #2 data:')
# print(models[1].firstChild.data)
# print(models[1].childNodes[0].data)

# # all items data
# print('\nAll model data:')
# for elem in models:
#   print(elem.firstChild.data)

