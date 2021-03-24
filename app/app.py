import json
import sqlite3

from pathlib import Path

from flask import Flask, render_template, g, redirect, url_for
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


@app.route('/')
def index():
    return redirect(url_for('schip'))


@app.route('/schip/')
def schip():
    return render_template('schip.html', active_page='schip')


@app.route('/trips/')
def trips():
    return render_template('trips.html', active_page='trips', trips=query_db('SELECT * FROM trips ORDER BY year DESC '))


@app.route('/live/')
def live():
    return render_template('live.html', active_page='live')


@app.route('/trips/<trip_name>/')
def trip(trip_name=None):
    trips = query_db("SELECT * FROM trips WHERE name=?", (trip_name,))
    if len(trips) == 0:
        abort(404)

    trip_record = trips[0]
    stops = json.loads(trip_record['stops'])
    coordinates = json.loads(trip_record['coordinates'])
    stop_indices = [stop['index'] for stop in stops]

    context = {
        'trip_label': trip_record['label'],
        'track_coordinates': coordinates,
        'stops': stops,
        'stop_indices': stop_indices,
    }

    return render_template('trip.html', active_page='trips', **context)
