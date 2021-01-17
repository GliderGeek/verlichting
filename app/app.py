import json
import sqlite3

from pathlib import Path

from flask import Flask, render_template, g
from werkzeug.exceptions import abort

app = Flask(__name__)

DATABASE = Path(__file__).parent / 'trips.sqlite'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row

    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route('/trips/')
def trips():
    return render_template('trips.html', trips=query_db('SELECT * FROM trips'))


@app.route('/trips/<trip_name>/')
def trip(trip_name=None):

    # TODO: create correct query
    trip = None
    for trip_row in query_db('SELECT * FROM trips'):
        if trip_row['name'] == trip_name:
            trip = trip_row
            break

    if trip is None:
        abort(404)

    stops = json.loads(trip['stops'])
    coordinates = json.loads(trip['coordinates'])
    stop_indices = [stop['index'] for stop in stops]

    context = {
        'trip_label': trip['label'],
        'track_coordinates': coordinates,
        'stops': stops,
        'stop_indices': stop_indices,
    }

    return render_template('trip.html', **context)
