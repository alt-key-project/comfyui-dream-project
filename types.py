class SharedTypes:
    current_frame = {"current_frame": ("INT", {"forceInput": True, "default": 0, "min": 0, "max": 24 * 3600 * 60})}
    frame_progress = {"frame_progress": ("FLOAT", {"forceInput": True, "default": 0, "min": 0.0, "max": 1.0})}
