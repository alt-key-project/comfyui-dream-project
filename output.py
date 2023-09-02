import json
from PIL.PngImagePlugin import PngInfo
from .categories import NodeCategories

from .types import SharedTypes, FrameCounter
from .shared import hashed_as_strings, convertTensorImageToPIL, DreamImageProcessor, DreamImage
import os


def _save_png(pil_image, filepath, embed_info, prompt, extra_pnginfo):
    info = PngInfo()
    if extra_pnginfo is not None:
        for item in extra_pnginfo:
            info.add_text(item, json.dumps(extra_pnginfo[item]))
    if prompt is not None:
        info.add_text("prompt", json.dumps(prompt))
    if embed_info:
        pil_image.save(filepath, pnginfo=info, optimize=True)
    else:
        pil_image.save(filepath, optimize=True)


def _save_jpg(pil_image, filepath, quality):
    pil_image.save(filepath, quality=quality, optimize=True)


class DreamNamedImageSaver:
    NODE_NAME = "Named Image Saver"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "directory_path": ("STRING", {"default": '', "multiline": False}),
                "filename": ("STRING", {"default": 'image.png', "multiline": False}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    CATEGORY = NodeCategories.IMAGE
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    RETURN_NAMES = ()
    FUNCTION = "save"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def save(self, filename, image, directory_path, extra_pnginfo, prompt):
        filepath = os.path.join(directory_path, filename)
        if len(image) != 1:
            print("Warning - batch output not supported for named image saver. Only saving first result!")
        pil_image = convertTensorImageToPIL(image[0])
        if not os.path.isdir(directory_path):
            os.makedirs(directory_path)
        filetype = os.path.splitext(filename)[1].lower()
        if filetype == ".png":
            _save_png(pil_image, filepath, True, prompt, extra_pnginfo)
        elif filetype in (".jpg", ".jpeg"):
            _save_jpg(pil_image, filepath, 98)
        else:
            print("Unsupported image type for saving - '{}'!".format(filetype))
            return ()
        print("Saved {} in {}".format(filename, os.path.abspath(directory_path)))
        return ()


class DreamImageSequenceOutput:
    NODE_NAME = "Image Sequence Saver"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.frame_counter | {
                "image": ("IMAGE",),
                "directory_path": ("STRING", {"default": '', "multiline": False}),
                "prefix": ("STRING", {"default": 'frame', "multiline": False}),
                "digits": ("INT", {"default": 5}),
                "filetype": (['png with embedded workflow', "png", 'jpg small size', 'jpg high quality'],),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    CATEGORY = NodeCategories.IMAGE_ANIMATION
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    RETURN_NAMES = ()
    FUNCTION = "save"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def _get_new_filename(self, current_frame, prefix, digits, filetype):
        return prefix + "_" + str(current_frame).zfill(digits) + "." + filetype.split(" ")[0]

    def _save_single_image(self, dream_image: DreamImage, batch_counter, frame_counter: FrameCounter, directory_path,
                           prefix, digits, filetype, prompt, extra_pnginfo):
        filename = self._get_new_filename(frame_counter.current_frame, prefix, digits, filetype)
        print("SAVE " + filename)
        if batch_counter >= 0:
            filepath = os.path.join(directory_path, "batch_" + (str(batch_counter).zfill(4)), filename)
        else:
            filepath = os.path.join(directory_path, filename)
        save_dir = os.path.dirname(filepath)
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)
        if filetype.startswith("png"):
            dream_image.save_png(filepath, filetype == 'png with embedded workflow', prompt, extra_pnginfo)
        elif filetype == "jpg small size":
            dream_image.save_jpg(filepath, 70)
        elif filetype == "jpg high quality":
            dream_image.save_jpg(filepath, 98)
        print("Saved {} in {}".format(filename, os.path.abspath(save_dir)))
        return ()

    def save(self, image, **args):
        proc = DreamImageProcessor(image, **args)
        proc.process(self._save_single_image)
        return ()
