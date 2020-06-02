from flask import Flask, render_template
from workflow.make_figures import make_start_end_figure, make_tracks_figure

from bokeh.embed import server_document
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
from threading import Thread


def spawnapp(doc):
    make_start_end_figure(doc)


def tracksapp(doc):
    make_tracks_figure(doc)


def bk_worker():
    server = Server({'/spawns': spawnapp, '/tracks': tracksapp}, io_loop=IOLoop(),
                    host="hurricanes-visualization.herokuapp.com", port="$PORT",
                    allow_websocket_origin=["https://hurricanes-visualization.herokuapp.com/"],
                    usexheaders=True)
    server.start()
    server.io_loop.start()


if __name__ == '__main__':
    Thread(target=bk_worker).start()
