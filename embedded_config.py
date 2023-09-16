EMBEDDED_CONFIGURATION = {
    "ffmpeg": {
        "file_extension": "mp4",
        "path": "ffmpeg",
        "arguments": ["-r", "%FPS%", "-f", "concat", "-safe", "0", "-vsync",
                      "cfr", "-i", "%FRAMES%", "-c:v", "libx264", "-pix_fmt",
                      "yuv420p", "%OUTPUT%"]
    },
    "mpeg_coder": {
        "encoding_threads": 4,
        "bitrate_factor": 1.0,
        "max_b_frame": 2,
        "file_extension": "mp4",
        "codec_name": "libx264"
    },
    "encoding": {
        "jpeg_quality": 95
    },
    "debug": False,
    "ui": {
        "top_category": "Dream",
        "prepend_icon_to_category": True,
        "append_icon_to_category": False,
        "prepend_icon_to_node": True,
        "append_icon_to_node": False,
        "category_icons": {
            "animation": "🎥",
            "postprocessing": "⚙",
            "transforms": "🔀",
            "curves": "📈",
            "color": "🎨",
            "generate": "⚡",
            "utils": "🛠",
            "image": "🌄",
            "switches": "⭆",
            "conditioning": "☯",
            "Dream": "✨"
        }
    },

}
