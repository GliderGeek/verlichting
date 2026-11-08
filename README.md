# verlichting
source for sailboat website, using flask for server side rendering of the pages

## Run locally
Requires Python 3.11–3.12 (3.11 is the oldest Python still receiving security fixes, `pandas==2.2.2` has no wheels for 3.13+; `.python-version` selects 3.12) and [uv](https://docs.astral.sh/uv/). Dependencies are defined in `app/pyproject.toml` and locked in `app/uv.lock`.

- inside app folder, install dependencies: `uv sync` (creates `.venv` with a compatible Python)
- inside app folder, run with flask (development): `uv run flask run`

## Run in production
- inside app folder: `uv run gunicorn -b 0.0.0.0:8000 app:app`

## Add new track
- run script `scripts/parse_gpx.py` with filename of gpx
- add json outputs in new row in db
- run locally
- modify stops in db
