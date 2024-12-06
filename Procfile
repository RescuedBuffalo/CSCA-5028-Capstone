web: gunicorn app.run:app
release: flask db upgrade
worker: python scripts/worker.py