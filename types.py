# -*- coding: utf-8 -*-
import random
import time

from typing import List, Dict, Tuple

from .shared import DreamImage


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

    def _calculate_channel_contrast(self, c):
        hist = list(map(lambda _: 0, range(16)))
        for pixel in self._colors:
            hist[pixel[c] // 16] += 1
        s = 0
        max_possible = (15 - 0) * (len(self) // 2) * (len(self) // 2)
        for i in range(16):
            for j in range(i):
                if i != j:
                    s += abs(i - j) * hist[i] * hist[j]
        return s / max_possible

    def _calculate_combined_contrast(self):
        s = 0
        for c in range(3):
            s += self._calculate_channel_contrast(c)
        return s / 3

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
        return ((r + g + b) / 3.0, self._calculate_combined_contrast(), r, g, b)

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


class PartialPrompt:
    ID = "PARTIAL_PROMPT"

    def __init__(self):
        self._data = {}

    def add(self, text: str, weight: float):
        output = PartialPrompt()
        output._data = dict(self._data)
        for parts in text.split(","):
            parts = parts.strip()
            if " " in parts:
                output._data["(" + parts + ")"] = weight
            else:
                output._data[parts] = weight
        return output

    def is_empty(self):
        return not self._data

    def abs_sum(self):
        if not self._data:
            return 0.0
        return sum(map(abs, self._data.values()))

    def abs_max(self):
        if not self._data:
            return 0.0
        return max(map(abs, self._data.values()))

    def scaled_by(self, f: float):
        new_data = PartialPrompt()
        new_data._data = dict(self._data)
        for text, weight in new_data._data.items():
            new_data._data[text] = weight * f
        return new_data

    def finalize(self, clamp: float):
        items = self._data.items()
        items = sorted(items, key=lambda pair: (pair[1], pair[0]))
        pos = list()
        neg = list()
        for text, w in sorted(items, key=lambda pair: (-pair[1], pair[0])):
            if w >= 0.0001:
                pos.append("({}:{:.3f})".format(text, min(clamp, w)))
        for text, w in sorted(items, key=lambda pair: (pair[1], pair[0])):
            if w <= -0.0001:
                neg.append("({}:{:.3f})".format(text, min(clamp, -w)))
        return ", ".join(pos), ", ".join(neg)


class LogEntry:
    ID = "LOG_ENTRY"

    @classmethod
    def new(cls, text):
        return LogEntry([(time.time(), text)])

    def __init__(self, data: List[Tuple[float, str]] = None):
        if data is None:
            self._data = list()
        else:
            self._data = list(data)

    def add(self, text: str):
        new_data = list(self._data)
        new_data.append((time.time(), text))
        return LogEntry(new_data)

    def merge(self, log_entry):
        new_data = list(self._data)
        new_data.extend(log_entry._data)
        return LogEntry(new_data)

    def get_filtered_entries(self, t: float):
        for d in sorted(self._data):
            if d[0] > t:
                yield d


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
    def total_time_in_seconds(self):
        return float(self.total_frames) / self.frames_per_second

    @property
    def remaining_time_in_seconds(self):
        return self.total_time_in_seconds - self.current_time_in_seconds

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
    frame_counter = {"frame_counter": (FrameCounter.ID,)}
    sequence = {"sequence": (AnimationSequence.ID,)}
    palette = {"palette": (RGBPalette.ID,)}
