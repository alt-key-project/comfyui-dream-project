import os, json
from .shared import DreamConfig

DEFAULT_CONFIG = {
    "ffmpeg": {
        "path": "ffmpeg",
        "arguments": ["-r", "%FPS%", "-f", "concat", "-safe", "0", "-i", "%FRAMES%", "-c:v", "libx265", "-pix_fmt",
             "yuv420p", "%OUTPUT%"]
    }
}


def run_install():
    if not os.path.isfile(DreamConfig.FILEPATH):
        with open(DreamConfig.FILEPATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)


if __name__ == "__main__":
    run_install()
