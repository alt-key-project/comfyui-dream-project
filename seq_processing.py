# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
import tempfile
from functools import lru_cache

from PIL import Image as PilImage

from .categories import NodeCategories
from .err import on_error
from .shared import DreamConfig, MpegEncoderUtility
from .types import *

CONFIG = DreamConfig()


@lru_cache(5)
def _load_image_cached(filename):
    return PilImage.open(filename)


class TempFileSet:
    def __init__(self):
        self._files = dict()

    def add(self, temppath, finalpath):
        self._files[temppath] = finalpath

    def remove(self):
        for f in self._files.keys():
            os.unlink(f)

    def finalize(self):
        for a, b in self._files.items():
            shutil.move(a, b)
        self._files = dict()


class AnimationSeqProcessor:
    def __init__(self, sequence: AnimationSequence):
        self._sequence = sequence
        self._input_cache = {}
        self._inputs = {}
        self._output_dirs = {}
        for b in self._sequence.batches:
            self._inputs[b] = list(self._sequence.get_image_files_of_batch(b))
            self._output_dirs[b] = os.path.dirname(os.path.abspath(self._inputs[b][0]))
        self._ext = os.path.splitext(self._inputs[0][0])[1].lower()
        self._length = len(self._inputs[0])

    def _load_input(self, batch_id, index) -> DreamImage:
        files = self._inputs[batch_id]
        index = min(max(0, index), len(files) - 1)
        filename = files[index]
        return DreamImage(pil_image=_load_image_cached(filename))

    def _process_single_batch(self, batch_id, indices, index_offsets: List[int], fun, output_dir) -> List[str]:
        all_indices = list(indices)
        last_index = max(all_indices)
        workset = TempFileSet()
        rnd = random.randint(0, 1000000)
        result_files = list()
        try:
            for index in all_indices:
                images = list(map(lambda offset: self._load_input(batch_id, index + offset), index_offsets))

                result: Dict[int, DreamImage] = fun(index, last_index, images)
                for (result_index, img) in result.items():
                    filepath = os.path.join(output_dir,
                                            "tmp_" + str(rnd) + "_" + (str(result_index).zfill(8)) + self._ext)
                    filepath_final = os.path.join(output_dir, "seq_" + (str(result_index).zfill(8)) + self._ext)
                    if self._ext == ".png":
                        img.save_png(filepath)
                    else:
                        img.save_jpg(filepath, quality=CONFIG.get("encoding.jpeg_quality", 98))
                    workset.add(filepath, filepath_final)
                    result_files.append(filepath_final)
            # all done with batch - remove input files
            for oldfile in self._inputs[batch_id]:
                os.unlink(oldfile)
            workset.finalize()
            return result_files
        finally:
            workset.remove()

    def process(self, index_offsets: List[int], fun):
        results = dict()
        new_length = 0
        for batch_id in self._sequence.batches:
            resulting_filenames = self._process_single_batch(batch_id, range(len(self._inputs[batch_id])),
                                                             index_offsets, fun,
                                                             self._output_dirs[batch_id])
            for (index, filename) in enumerate(resulting_filenames):
                l = results.get(index, [])
                l.append(filename)
                results[index] = l
            new_length = len(resulting_filenames)
        new_fps = self._sequence.frame_counter.frames_per_second * (float(new_length) / self._length)
        counter = FrameCounter(new_length - 1, new_length, new_fps)
        return AnimationSequence(counter, results)


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

        subprocess.check_output(cmd, shell=True)
    finally:
        os.unlink(tempfilepath)


def _make_video_filename(name, file_ext):
    (b, _) = os.path.splitext(name)
    return b + "." + file_ext.strip(".")


class DreamVideoEncoderMpegCoder:
    NODE_NAME = "Video Encoder (mpegCoder)"
    ICON = "🎬"
    CATEGORY = NodeCategories.ANIMATION_POSTPROCESSING
    RETURN_TYPES = (LogEntry.ID,)
    RETURN_NAMES = ("log_entry",)
    OUTPUT_NODE = True
    FUNCTION = "encode"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.sequence | {
                "name": ("STRING", {"default": 'video', "multiline": False}),
                "framerate_factor": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 100.0}),
                "remove_images": ("BOOLEAN", {"default": True})
            },
        }

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

    def encode(self, sequence, name, framerate_factor, remove_images):
        if not sequence.is_defined:
            return (LogEntry([]),)
        config = DreamConfig()
        filename = _make_video_filename(name, config.get("mpeg_coder.file_extension", "mp4"))
        log_entry = LogEntry([])
        for batch_num in sequence.batches:
            try:
                images = list(sequence.get_image_files_of_batch(batch_num))
                filename = self._find_free_filename(filename, os.path.dirname(images[0]))
                first_image = DreamImage.from_file(images[0])
                enc = MpegEncoderUtility(video_path=filename,
                                         bit_rate_factor=float(config.get("mpeg_coder.bitrate_factor", 1.0)),
                                         encoding_threads=int(config.get("mpeg_coder.encoding_threads", 4)),
                                         max_b_frame=int(config.get("mpeg_coder.max_b_frame", 2)),
                                         width=first_image.width,
                                         height=first_image.height,
                                         files=images,
                                         fps=sequence.fps * framerate_factor,
                                         codec_name=config.get("mpeg_coder.codec_name", "libx265"))
                enc.encode()
                log_entry = log_entry.add("Generated video '{}'".format(filename))
                if remove_images:
                    for imagepath in images:
                        if os.path.isfile(imagepath):
                            os.unlink(imagepath)
            except Exception as e:
                on_error(self.__class__, str(e))
        return (log_entry,)


class DreamVideoEncoder:
    NODE_NAME = "FFMPEG Video Encoder"
    DISPLAY_NAME = "Video Encoder (FFMPEG)"
    ICON = "🎬"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.sequence | {
                "name": ("STRING", {"default": 'video', "multiline": False}),
                "framerate_factor": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 100.0}),
                "remove_images": ("BOOLEAN", {"default": True})
            },
        }

    CATEGORY = NodeCategories.ANIMATION_POSTPROCESSING
    RETURN_TYPES = (LogEntry.ID,)
    RETURN_NAMES = ("log_entry",)
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
        return filename

    def encode(self, sequence: AnimationSequence, name: str, remove_images, framerate_factor):
        if not sequence.is_defined:
            return (LogEntry([]),)

        config = DreamConfig()
        filename = _make_video_filename(name, config.get("ffmpeg.file_extension", "mp4"))
        log_entry = LogEntry([])
        for batch_num in sequence.batches:
            try:
                images = list(sequence.get_image_files_of_batch(batch_num))
                actual_filename = self.generate_video(images, sequence.fps * framerate_factor, filename, config)

                log_entry = log_entry.add("Generated video '{}'".format(actual_filename))
                if remove_images:
                    for imagepath in images:
                        if os.path.isfile(imagepath):
                            os.unlink(imagepath)
            except Exception as e:
                on_error(self.__class__, str(e))
        return (log_entry,)


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

    def process(self, sequence: AnimationSequence, multiplier):
        if not sequence.is_defined:
            return (sequence,)

        def _generate_extra_frames(input_index, last_index, images):
            results = {}
            if input_index == last_index:
                # special case
                for i in range(multiplier):
                    results[input_index * multiplier + i] = images[0]
                return results

            # normal case
            current_frame = images[0]
            next_frame = images[1]
            for i in range(multiplier):
                alpha = float(i + 1) / multiplier
                results[multiplier * input_index + i] = current_frame.blend(next_frame, 1.0 - alpha, alpha)
            return results

        proc = AnimationSeqProcessor(sequence)
        return (proc.process([0, 1], _generate_extra_frames),)


class DreamSequenceBlend:
    NODE_NAME = "Image Sequence Blend"

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

        current_sequence = sequence
        for i in range(iterations):
            proc = AnimationSeqProcessor(current_sequence)

            def _blur(index: int, last_index: int, images: List[DreamImage]):
                pre_frame = images[0].blend(images[1], fade_in, 1.0)
                post_frame = images[2].blend(images[1], fade_out, 1.0)
                return {index: pre_frame.blend(post_frame)}

            current_sequence = proc.process([-1, 0, 1], _blur)

        return (current_sequence,)
