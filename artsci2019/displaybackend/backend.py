from multiprocessing import Process
from artsci2019.lib.portrait import PortraitGen
from artsci2019.lib.image_storage import write_recognized_frames


class Backend:

    def __init__(self, stack_size, pool_size, directory):
        self.portrait_gen = PortraitGen(stack_size, pool_size)
        self.target_directory = directory

    def update(self, recognized_frames):
        p = Process(target=write_recognized_frames, args=(self.target_directory, recognized_frames))
        p.start()
        changed = self.portrait_gen.update(recognized_frames)
        p.join()
        return changed

    def get_portrait(self):
        return self.portrait_gen.portrait_frame
