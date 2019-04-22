from multiprocessing import Process
from artsci2019.backend.portrait import PortraitGen
from artsci2019.backend.image_storage import ImageStorage


class Backend:

    def __init__(self, stack_size, pool_size, directory):
        self.portrait_gen = PortraitGen(stack_size, pool_size)
        self.image_storage = ImageStorage(directory)

    def update(self, recognized_frames):
        p = Process(target=self.image_storage.update, args=(recognized_frames,))
        p.start()
        changed = self.portrait_gen.update(recognized_frames)
        p.join()
        return changed

    def get_portrait(self):
        return self.portrait_gen.portrait_frame