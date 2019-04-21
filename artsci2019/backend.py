from flask import Flask
from flask import request
from artsci2019.portrait import PortraitGen
import pickle


def create_app(stack_size, thread_count):
    app = Flask(__name__)
    pg = PortraitGen(stack_size, thread_count)

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

    return app
