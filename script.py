import gpxpy
import gpxpy.gpx
import pandas as pd
import plotly.express as px

from pathlib import Path

england_gpx = Path(__file__).parent / 'verlichting_tracks' / 'Engeland2016.gpx'
limfjord_gpx = Path(__file__).parent / 'verlichting_tracks' / 'Limfjord2018.gpx'
wadden_gpx = Path(__file__).parent / 'verlichting_tracks' / '2020Wadden.gpx'

class GPXSource:

	def __init__(self, path, start_index, end_index = None):
	    self.path = path
	    self.start_index = start_index
	    self.end_index = end_index


class Trip:
	def __init__(self, name, sources):
		self.name = name
		self.sources = sources

	def serialize(self) -> dict:

		lat = []
		lon = []
		trip_name = []

		for source in self.sources:
			gpx_file = open(source.path, 'r')
			gpx = gpxpy.parse(gpx_file)

			if source.end_index is None:
				segment_domain = gpx.tracks[0].segments[source.start_index::]
			else:
				segment_domain = gpx.tracks[0].segments[source.start_index:source.end_index]

			for segment in segment_domain:
				for point in segment.points:
					lat.append(point.latitude)
					lon.append(point.longitude)
					trip_name.append(self.name)

		return {'lat': lat, 'lon': lon, 'trip_name': trip_name}


trips = [
	Trip('Engeland 2016', [GPXSource(england_gpx, 0, 43)]),
	Trip('Dieppe 2017', [GPXSource(england_gpx, 61, 92)]),
	Trip('Denemarken 2018', [GPXSource(england_gpx, 99), GPXSource(limfjord_gpx, 0, 37)]),
	Trip('Kanaaleilanden 2019', [GPXSource(limfjord_gpx, 47, 109)]),
	Trip('wadden2020', [GPXSource(wadden_gpx, 6, -1)]),
]



def visualize_trips(trips):

	df = pd.DataFrame()

	for trip in trips:
		df_trip = pd.DataFrame(trip.serialize())

		df = pd.concat([df, df_trip])

# df = pd.DataFrame(trips[0].serialize())

	fig = px.line_mapbox(df, lat="lat", lon="lon", zoom=3, height=600, color='trip_name')

	fig.update_layout(mapbox_style="stamen-terrain", mapbox_zoom=4, mapbox_center_lat = 52.36, mapbox_center_lon=5.1,
	    margin={"r":0,"t":0,"l":0,"b":0})

	fig.show()

def write_trip_to_geojson(trip):

	import geojson
	import json

	df_trip = pd.DataFrame(trip.serialize())


	linestring_items = []
	for i, row in df_trip.iterrows():
		linestring_items.append((row['lon'], row['lat']))

	ls = geojson.LineString(linestring_items)

	with open(f'{trip.name}.json', 'w') as f:
		json.dump(ls, f)

	# print(ls)







# visualize_trips([trips[-1]])
write_trip_to_geojson(trips[-1])
