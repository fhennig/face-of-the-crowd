from flask import Flask
from flask import request
from artsci2019.backend.backend import Backend
import pickle


def create_app(stack_size, thread_count, directory):
    app = Flask(__name__)
    backend = Backend(stack_size, thread_count, directory)

    @app.route('/update', methods=['POST'])
    def update():
        # check if everything is okay
        if not request.method == 'POST':
            return 'ERROR'
        if 'params' not in request.files:
            return 'ERROR'
        # unpack params
        pickled_params = request.files['params']
        recognized_frames = pickle.load(pickled_params)
        changed = backend.update(recognized_frames)
        return str(changed)

    @app.route('/portrait', methods=['GET'])
    def get_portrait():
        s = pickle.dumps(backend.get_portrait())
        return s

    return app