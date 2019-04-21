from flask import Flask
from flask import request
from portrait import PortraitGen
import pickle


app = Flask(__name__)
pg = PortraitGen(10, 4)


@app.route('/update', methods=['POST'])
def update():
    if not request.method == 'POST':
        return 'ERROR'
    if 'params' not in request.files:
        return 'ERROR'
    pickled_params = request.files['params']
    params = pickle.load(pickled_params)
    changed = pg.update(params)
    return str(changed)


@app.route('/portrait', methods=['GET'])
def get_portrait():
    s = pickle.dumps(pg.portrait_frame)
    return s