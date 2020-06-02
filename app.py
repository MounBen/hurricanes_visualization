from flask import Flask, render_template
from workflow.make_figures import make_start_end_figure, make_tracks_figure

from bokeh.embed import server_document
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
from threading import Thread

app = Flask(__name__)


def spawnapp(doc):
    make_start_end_figure(doc)


def tracksapp(doc):
    make_tracks_figure(doc)


@app.route('/', methods=['GET'])
def home():
    return render_template("index.html", template="Flask")


@app.route('/spawns/', methods=['GET'])
def spawn_page():
    script = server_document('/spawns')
    return render_template("embed.html", script=script, template="Flask")


@app.route('/tracks/', methods=['GET'])
def tracks_page():
    script = server_document('/tracks')
    return render_template("embed.html", script=script, template="Flask")


def bk_worker():
    server = Server({'/spawns': spawnapp, '/tracks': tracksapp}, io_loop=IOLoop(),
                    host="hurricanes-visualization.herokuapp.com", port="$PORT",
                    allow_websocket_origin=["https://hurricanes-visualization.herokuapp.com/*",
                                            "localhost:8000"],
                    usexheaders=True)
    server.start()
    server.io_loop.start()


Thread(target=bk_worker).start()

if __name__ == '__main__':
    app.run(threaded=True, port=33507)
