web: gunicorn app:app --log-level=debug

worker: bokeh serve --port=$PORT --num-procs=0 --allow-websocket-origin=hurricanes-visualization.herokuapp.com \
        --address=0.0.0.0 --use-xheaders app.py