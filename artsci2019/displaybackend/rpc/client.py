import requests
import pickle
import io


class RemoteBackend:

    def __init__(self, host, port):
        """A wrapper for the RPC with the server"""
        self.host = host
        self.port = port

    def update(self, recognized_frames):
        """Takes a list of recognized frames and adds them to the rpc."""
        url = 'http://{}:{}/update'.format(self.host, self.port)
        bytesIO = io.BytesIO()
        pickle.dump(recognized_frames, bytesIO)
        bytesIO.seek(0)
        files = {'params': bytesIO}
        print("Posting request")
        resp = requests.post(url, files=files)
        if resp.content == b'False':
            return False
        elif resp.content == b'True':
            return True
        else:
            raise ValueError()

    def get_portrait(self):
        url = 'http://{}:{}/portrait'.format(self.host, self.port)
        resp = requests.get(url)
        frame = pickle.loads(resp.content)
        return frame
