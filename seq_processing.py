from .types import *
from .categories import NodeCategories
from .shared import DreamConfig
import os, tempfile, subprocess


def _ffmpeg(config, filenames, fps, output):
    fps = float(fps)
    duration = 1.0 / fps
    tmp = tempfile.NamedTemporaryFile(delete=False, mode="wb")
    tempfilepath = tmp.name
    try:
        for filename in filenames:
            filename = filename.replace("\\", "/")
            tmp.write(f"file '{filename}'\n".encode())
            tmp.write(f"duration {duration}\n".encode())
    finally:
        tmp.close()

    try:
        cmd = [config.get("ffmpeg.path", "ffmpeg")]
        cmd.extend(config.get("ffmpeg.arguments"))
        replacements = {"%FPS%": str(fps), "%FRAMES%": tempfilepath, "%OUTPUT%": output}

        for (key, value) in replacements.items():
            cmd = list(map(lambda s: s.replace(key, value), cmd))

        subprocess.run(cmd, shell=True)
    finally:
        os.unlink(tempfilepath)


class DreamVideoEncoder:
    NODE_NAME = "FFMPEG Video Encoder"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.sequence | {
                "filename": ("STRING", {"default": 'video.mp4', "multiline": False}),
                "remove_images": (["yes", "no"],)
            },
        }

    CATEGORY = NodeCategories.ANIMATION_POSTPROCESSING
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    OUTPUT_NODE = True
    FUNCTION = "encode"

    @classmethod
    def IS_CHANGED(cls, sequence: AnimationSequence, **kwargs):
        return sequence.is_defined

    def _find_free_filename(self, filename, defaultdir):
        if os.path.basename(filename) == filename:
            filename = os.path.join(defaultdir, filename)
        n = 1
        tested = filename
        while os.path.exists(tested):
            n += 1
            (b, ext) = os.path.splitext(filename)
            tested = b + "_" + str(n) + ext
        return tested

    def generate_video(self, files, fps, filename, config):
        filename = self._find_free_filename(filename, os.path.dirname(files[0]))
        _ffmpeg(config, files, fps, filename)

    def encode(self, sequence: AnimationSequence, filename: str, remove_images):
        if not sequence.is_defined:
            return ()

        config = DreamConfig()
        for batch_num in sequence.batches:
            try:
                images = list(sequence.get_image_files_of_batch(batch_num))
                self.generate_video(images, sequence.fps, filename, config)
                if remove_images == "yes":
                    for imagepath in images:
                        if os.path.isfile(imagepath):
                            os.unlink(imagepath)
            except Exception as e:
                print("Failed to encode files in dir {}!".format(os.path.dirname(images[0])))
                print(str(e))
        return ()


class DreamSequenceTweening:
    NODE_NAME = "Image Sequence Tweening"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.sequence | {
                "multiplier": ("INT", {"default": 2, "min": 2, "max": 10}),
            },
        }

    CATEGORY = NodeCategories.ANIMATION_POSTPROCESSING
    RETURN_TYPES = (AnimationSequence.ID,)
    RETURN_NAMES = ("sequence",)
    OUTPUT_NODE = False
    FUNCTION = "process"

    @classmethod
    def IS_CHANGED(cls, sequence: AnimationSequence, **kwargs):
        return sequence.is_defined

    def process(self, sequence: AnimationSequence):
        if not sequence.is_defined:
            return (sequence,)

        return (sequence,)


class DreamSequenceBlur:
    NODE_NAME = "Image Sequence Blur"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.sequence | {
                "fade_in": ("FLOAT", {"default": 0.1, "min": 0.01, "max": 0.5}),
                "fade_out": ("FLOAT", {"default": 0.1, "min": 0.01, "max": 0.5}),
                "iterations": ("INT", {"default": 1, "min": 1, "max": 10}),
            },
        }

    CATEGORY = NodeCategories.ANIMATION_POSTPROCESSING
    RETURN_TYPES = (AnimationSequence.ID,)
    RETURN_NAMES = ("sequence",)
    OUTPUT_NODE = False
    FUNCTION = "process"

    @classmethod
    def IS_CHANGED(cls, sequence: AnimationSequence, **kwargs):
        return sequence.is_defined

    def process(self, sequence: AnimationSequence, fade_in, fade_out, iterations):
        if not sequence.is_defined:
            return (sequence,)

        return (sequence,)
