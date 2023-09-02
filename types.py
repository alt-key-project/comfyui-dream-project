class FrameCounter:
    ID = "FRAME_COUNTER"

    def __init__(self, current_frame=0, total_frames=1, frames_per_second=25):
        self.current_frame = max(0, current_frame)
        self.total_frames = max(total_frames, 1)
        self.frames_per_second = max(1, frames_per_second)

    def incremented(self, amount: int):
        return FrameCounter(self.current_frame + amount, self.total_frames, self.frames_per_second)

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


class SharedTypes:
    frame_counter = {"frame_counter": (FrameCounter.ID, {"forceInput": True})}
