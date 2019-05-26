import pyaudio
import wave


class SoundPlayer:

    # https://stackoverflow.com/questions/17657103/how-to-play-wav-file-in-python

    def __init__(self, filename):
        self.filename = filename

    def play(self):
        chunk = 1024
        f = wave.open(self.filename, "rb")
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                        channels=f.getnchannels(),
                        rate=f.getframerate(),
                        output=True)
        data = f.readframes(chunk)
        while data:
            stream.write(data)
            data = f.readframes(chunk)
        stream.stop_stream()
        stream.close()
        p.terminate()
