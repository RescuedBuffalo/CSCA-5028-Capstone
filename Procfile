web: gunicorn app.run:app
release: flask db upgrade
worker: python app.scripts.worker.py