class AKPFrameCount:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "primitive_input": ("INT", {"default": 0, "min": 0, "max": 24 * 3600 * 60}),
                "total_frames": ("INT", {"default": 100, "min": 1, "max": 24 * 3600 * 60}),
            },
        }

    CATEGORY = "AKP Animation"
    RETURN_TYPES = ("INT", "FLOAT")
    RETURN_NAMES = ("current_frame", "frame_progress")
    FUNCTION = "result"

    def result(self, primitive_input, total_frames):
        primitive_input = min(max(0, primitive_input), total_frames - 1)
        return (primitive_input, primitive_input / float(total_frames - 1))
