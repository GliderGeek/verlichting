# verlichting
source for sailboat website, using flask for server side rendering of the pages

## Run locally
- install dependencies inside virtualenv. inside app folder: `pip install -r requirements.txt`
- run with flask. inside app folder: `flask run`

## Add new track
- run script `scripts/parse_gpx.py` with filename of gpx
- add json outputs in new row in db
- run locally
- modify stops in db
