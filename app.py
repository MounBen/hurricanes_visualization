try:
    import asyncio
except ImportError:
    raise RuntimeError("This example requries Python3 / asyncio")


from workflow.make_figures import make_start_end_figure, make_tracks_figure

from tornado.ioloop import IOLoop
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.server.server import BaseServer
from bokeh.server.tornado import BokehTornado
from bokeh.server.util import bind_sockets
from tornado.httpserver import HTTPServer
from threading import Thread


spawnapp = Application(FunctionHandler(make_start_end_figure))


tracksapp = Application(FunctionHandler(make_tracks_figure))


# This is so that if this app is run using something like "gunicorn -w 4" then
# each process will listen on its own port
sockets, port = bind_sockets("localhost", 0)


def bk_worker():
    asyncio.set_event_loop(asyncio.new_event_loop())

    bokeh_tornado = BokehTornado({'/spawns': spawnapp, '/tracks': tracksapp},
                                 extra_websocket_origins=["localhost:5006"])
    bokeh_http = HTTPServer(bokeh_tornado)
    bokeh_http.add_sockets(sockets)

    server = BaseServer(IOLoop.current(), bokeh_tornado, bokeh_http)
    server.start()
    server.io_loop.start()
    print('hahaha')


if __name__ == '__main__':

    t = Thread(target=bk_worker)
    t.daemon = True
    t.start()
