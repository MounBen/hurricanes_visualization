from flask import Flask, render_template

from bokeh.embed import server_document

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template("index.html", template="Flask")


@app.route('/spawns/', methods=['GET'])
def spawn_page():
    script = server_document('https://hurricanes-bokeh.herokuapp.com/spawns')
    return render_template("embed.html", script=script, template="Flask")


@app.route('/tracks/', methods=['GET'])
def tracks_page():
    script = server_document('https://hurricanes-bokeh.herokuapp.com/tracks')
    return render_template("embed.html", script=script, template="Flask")


if __name__ == '__main__':
    app.run(threaded=True)
