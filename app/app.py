import json
import sqlite3

from pathlib import Path

from flask import Flask, render_template, g, redirect, url_for, request, jsonify
from werkzeug.exceptions import abort

app = Flask(__name__)

DATABASE = Path(__file__).parent / 'trips.sqlite'

REPAIR_DB = Path(__file__).parent / 'repairdata.sqlite'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row

    return db


def get_repair_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(REPAIR_DB)
    db.row_factory = sqlite3.Row
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def query_repair_db(query, args=(), one=False):
    cur = get_repair_db().execute(query, args)
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


def filter(**kwargs):
    filter_clause = ''
    if len(kwargs) > 0:
        first = True
        for key, val in kwargs.items():
            if first:
                filter_clause = filter_clause + f"WHERE {key}='{val}'"
                first = False
                print('here1')
            else:
                filter_clause = filter_clause + f" AND {key}='{val}'"
                print('here2')
    return filter_clause


@app.route('/brands/')
def brands():

    filters = {}
    model = request.args.get('model')
    kind_of_product = request.args.get('kind')
    if model not in (None, ''):
        filters['model'] = model
    if kind_of_product not in (None, ''):
        filters['kind_of_product'] = kind_of_product

    query = f'SELECT DISTINCT brand FROM repairs {filter(**filters)} ORDER BY brand ASC '

    print(query)

    return jsonify([row['brand'] for row in query_repair_db(query)])


@app.route('/models/')
def models():

    filters = {}
    brand = request.args.get('brand')
    kind_of_product = request.args.get('kind')
    if brand not in (None, ''):
        filters['brand'] = brand
    if kind_of_product not in (None, ''):
        filters['kind_of_product'] = kind_of_product

    query = f'SELECT DISTINCT model FROM repairs {filter(**filters)} ORDER BY model ASC '

    print('query:', query)

    return jsonify([row['model'] for row in query_repair_db(query)])


@app.route('/kinds/')
def kinds():
    filters = {}
    brand = request.args.get('brand')
    model = request.args.get('model')
    if brand not in (None, ''):
        filters['brand'] = brand
    if model not in (None, ''):
        filters['model'] = model

    query = f'SELECT DISTINCT kind_of_product FROM repairs {filter(**filters)} ORDER BY kind_of_product ASC '
    return jsonify([row['kind_of_product'] for row in query_repair_db(query)])


@app.route('/repair/')
def repair():
    brands = [row['brand'] for row in query_repair_db('SELECT DISTINCT brand FROM repairs ORDER BY brand ASC ')]
    models = [row['model'] for row in query_repair_db('SELECT DISTINCT model FROM repairs ORDER BY model ASC ')]
    product_kinds = [row['kind_of_product'] for row in query_repair_db('SELECT DISTINCT kind_of_product FROM repairs ORDER BY kind_of_product ASC ')]

    # todo
    # - resultaten echt tonen
    # - is performance afhankelijke opties goed genoeg?

    return render_template('repair.html', brands=brands, models=models, product_kinds=product_kinds)


@app.route('/repairs/')
def repairs():

    filters = {}
    brand = request.args.get('brand')
    model = request.args.get('model')
    kind_of_product = request.args.get('kind')
    if brand not in (None, ''):
        filters['brand'] = brand
    if model not in (None, ''):
        filters['model'] = model
    if kind_of_product not in (None, ''):
        filters['kind_of_product'] = kind_of_product

    # todo: address sql injection vuln
    query = f"SELECT COUNT(*) FROM repairs {filter(**filters)}"

    res = query_repair_db(query)
    number_of_results = (res[0]['COUNT(*)'])

    first_ten_query = f"SELECT brand, model, kind_of_product, [Repair id] FROM repairs {filter(**filters)} LIMIT 10"
    results = [{'brand': row['brand'],
                'model': row['model'],
                'kind': row['kind_of_product'],
                'link': f"/repairs/{row['Repair id']}",
                } for row in query_repair_db(first_ten_query)]
    return {'number_of_results': number_of_results, 'page_size': 10, 'results': results}


def serialize_row(row):
    return {
        'repair_id': row["Repair id"],
        'repair_date': row['Repair date'],
        'repair_cafe_number': row["Repair Cafe number"],
        'repair_cafe_name': row["Repair Cafe name"],
        'country': row["Country"],
        'kind': row['kind_of_product'],
        'category': row['Category'],
        'brand': row['brand'],
        'model': row['model'],
        'production_year': row['(Estimated) Year of production'],
        'problem_description': row["Problem description + probable cause"],
        'has_been_repaired': row['Has the product been repaired?'],
        'defect_found': row['Defect found'],
        'yes_repaired_actions': row["If yes: what did you do to repair it?"],
        'half_repaired_actions': row["If half repaired: what did you do, what advice did you give?"],
        'not_repaired_actions_list': row["If not repaired: why could you not repair it (list)?"],
        'not_repaired_actions_open': row["If not repaired: why could you not repair it (open answer)?"],
        'repairability': row["Reparability of product  (1 = difficult, 10 = easy)"],
        'repair_info_used': row["Did you use repair information?"],
        'location_repair_info': row["Where did this information come from?"],
        'url_repair_info': row["Source repair information (url website)"],
        'repair_suggestions': row["Do you have any suggestions for other repairers of this (or similar) product?"],
    }


@app.route('/repairs/<repair_id>')
def repair_item(repair_id):
    # todo: change into column name without space
    query = f"SELECT * FROM repairs WHERE [Repair id]='{repair_id}'"
    results = [row for row in query_repair_db(query)]

    print(len(results))
    if len(results) == 0:
        return 'not found'
    elif len(results) == 1:
        return serialize_row(results[0])
    else:
        raise ValueError('multiple')
