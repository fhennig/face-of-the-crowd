from artsci2019.backend.portrait import PortraitGen
from artsci2019.backend.image_storage import ImageStorage


class Backend:

    def __init__(self, stack_size, pool_size, directory):
        self.portrait_gen = PortraitGen(stack_size, pool_size)
        self.image_storage = ImageStorage(directory)

    def update(self, recognized_frames):
        changed = self.portrait_gen.update(recognized_frames)
        self.image_storage.update(recognized_frames)  # TODO parallelize
        return changed

    def get_portrait(self):
        return self.portrait_gen.portrait_frame