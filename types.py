from typing import List, Dict
from .shared import DreamImage
import random, time


class RGBPalette:
    ID = "RGB_PALETTE"

    def __init__(self, colors: List[tuple[int, int, int]] = None, image: DreamImage = None):
        self._colors = []

        def _fix_tuple(t):
            if len(t) < 3:
                return (t[0], t[0], t[0])
            else:
                return t

        if image:
            for p, _, _ in image:
                self._colors.append(_fix_tuple(p))
        if colors:
            for c in colors:
                self._colors.append(_fix_tuple(c))

    def analyze(self):
        total_red = 0
        total_blue = 0
        total_green = 0
        for pixel in self:
            total_red += pixel[0]
            total_green += pixel[1]
            total_blue += pixel[2]
        n = len(self._colors)
        r = float(total_red) / (255 * n)
        g = float(total_green) / (255 * n)
        b = float(total_blue) / (255 * n)
        return ((r + g + b) / 3.0, r, g, b)

    def __len__(self):
        return len(self._colors)

    def __iter__(self):
        return iter(self._colors)

    def random_iteration(self, seed=None):
        s = seed if seed is not None else int(time.time() * 1000)
        n = len(self._colors) - 1
        c = self._colors

        class _ColorIterator:
            def __init__(self):
                self._r = random.Random()
                self._r.seed(s)
                self._n = n
                self._c = c

            def __next__(self):
                return self._c[self._r.randint(0, self._n)]

        return _ColorIterator()


class FrameCounter:
    ID = "FRAME_COUNTER"

    def __init__(self, current_frame=0, total_frames=1, frames_per_second=25.0):
        self.current_frame = max(0, current_frame)
        self.total_frames = max(total_frames, 1)
        self.frames_per_second = float(max(1.0, frames_per_second))

    def incremented(self, amount: int):
        return FrameCounter(self.current_frame + amount, self.total_frames, self.frames_per_second)

    @property
    def is_first_frame(self):
        return self.current_frame == 0

    @property
    def is_final_frame(self):
        return (self.current_frame + 1) == self.total_frames

    @property
    def is_after_last_frame(self):
        return self.current_frame >= self.total_frames

    @property
    def current_time_in_seconds(self):
        return float(self.current_frame) / self.frames_per_second

    @property
    def progress(self):
        return float(self.current_frame) / (max(2, self.total_frames) - 1)


class AnimationSequence:
    ID = "ANIMATION_SEQUENCE"

    def __init__(self, frame_counter: FrameCounter, frames: Dict[int, List[str]] = None):
        self.frames = frames
        self.fps = frame_counter.frames_per_second
        self.frame_counter = frame_counter
        if self.is_defined:
            self.keys_in_order = sorted(frames.keys())
            self.num_batches = min(map(len, self.frames.values()))
        else:
            self.keys_in_order = []
            self.num_batches = 0

    @property
    def batches(self):
        return range(self.num_batches)

    def get_image_files_of_batch(self, batch_num):
        for key in self.keys_in_order:
            yield self.frames[key][batch_num]

    @property
    def is_defined(self):
        if self.frames:
            return True
        else:
            return False


class SharedTypes:
    frame_counter = {"frame_counter": (FrameCounter.ID, {"forceInput": True})}
    sequence = {"sequence": (AnimationSequence.ID, {"forceInput": True})}
    palette = {"palette": (RGBPalette.ID, {"forceInput": True})}
