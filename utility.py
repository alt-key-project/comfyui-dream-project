# -*- coding: utf-8 -*-
import datetime
import math
import os

import folder_paths as comfy_paths

from .categories import NodeCategories
from .shared import hashed_as_strings, DreamStateFile
from .types import LogEntry, SharedTypes, FrameCounter

_logfile_state = DreamStateFile("logging")


class DreamJoinLog:
    NODE_NAME = "Log Entry Joiner"
    ICON = "🗎"
    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = (LogEntry.ID,)
    RETURN_NAMES = ("log_entry",)
    FUNCTION = "convert"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "entry_0": (LogEntry.ID,),
                "entry_1": (LogEntry.ID,),
                "entry_2": (LogEntry.ID,),
                "entry_3": (LogEntry.ID,),
            }
        }

    def convert(self, **values):
        entry = LogEntry([])
        for i in range(4):
            txt = values.get("entry_" + str(i), None)
            if txt:
                entry = entry.merge(txt)
        return (entry,)


class DreamFloatToLog:
    NODE_NAME = "Float to Log Entry"
    ICON = "🗎"
    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = (LogEntry.ID,)
    RETURN_NAMES = ("log_entry",)
    FUNCTION = "convert"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("FLOAT", {"default": 0}),
                "label": ("STRING", {"default": ""}),
            },
        }

    def convert(self, label, value):
        return (LogEntry.new(label + ": " + str(value)),)


class DreamIntToLog:
    NODE_NAME = "Int to Log Entry"
    ICON = "🗎"
    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = (LogEntry.ID,)
    RETURN_NAMES = ("log_entry",)
    FUNCTION = "convert"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("INT", {"default": 0}),
                "label": ("STRING", {"default": ""}),
            },
        }

    def convert(self, label, value):
        return (LogEntry.new(label + ": " + str(value)),)


class DreamStringToLog:
    NODE_NAME = "String to Log Entry"
    ICON = "🗎"
    OUTPUT_NODE = True
    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = (LogEntry.ID,)
    RETURN_NAMES = ("log_entry",)
    FUNCTION = "convert"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": ""}),
            },
            "optional": {
                "label": ("STRING", {"default": ""}),
            }
        }

    def convert(self, text, **values):
        label = values.get("label", "")
        if label:
            return (LogEntry.new(label + ": " + text),)
        else:
            return (LogEntry.new(text),)


class DreamStringTokenizer:
    NODE_NAME = "String Tokenizer"
    ICON = "🪙"
    OUTPUT_NODE = True
    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("token",)
    FUNCTION = "exec"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "separator": ("STRING", {"default": ","}),
                "selected": ("INT", {"default": 0, "min": 0})
            },
        }

    def exec(self, text: str, separator: str, selected: int):
        if separator is None or separator == "":
            separator = " "
        parts = text.split(sep=separator)
        return (parts[abs(selected) % len(parts)].strip(),)


class DreamLogFile:
    NODE_NAME = "Log File"
    ICON = "🗎"
    OUTPUT_NODE = True
    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "write"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.frame_counter | {
                "log_directory": ("STRING", {"default": comfy_paths.output_directory}),
                "log_filename": ("STRING", {"default": "dreamlog.txt"}),
                "stdout": ("BOOLEAN", {"default": True}),
                "active": ("BOOLEAN", {"default": True}),
                "clock_has_24_hours": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "entry_0": (LogEntry.ID,),
                "entry_1": (LogEntry.ID,),
                "entry_2": (LogEntry.ID,),
                "entry_3": (LogEntry.ID,),
                "entry_4": (LogEntry.ID,),
                "entry_5": (LogEntry.ID,),
                "entry_6": (LogEntry.ID,),
                "entry_7": (LogEntry.ID,),
            },
        }

    def _path_to_log_file(self, log_directory, logfile):
        if os.path.isabs(logfile):
            return os.path.normpath(os.path.abspath(logfile))
        elif os.path.isabs(log_directory):
            return os.path.normpath(os.path.abspath(os.path.join(log_directory, logfile)))
        elif log_directory:
            return os.path.normpath(os.path.abspath(os.path.join(comfy_paths.output_directory, log_directory, logfile)))
        else:
            return os.path.normpath(os.path.abspath(os.path.join(comfy_paths.output_directory, logfile)))

    def _get_tm_format(self, clock_has_24_hours):
        if clock_has_24_hours:
            return "%a %H:%M:%S"
        else:
            return "%a %I:%M:%S %p"

    def write(self, frame_counter: FrameCounter, log_directory, log_filename, stdout, active, clock_has_24_hours,
              **entries):
        if not active:
            return ()
        log_entry = None
        for i in range(8):
            e = entries.get("entry_" + str(i), None)
            if e is not None:
                if log_entry is None:
                    log_entry = e
                else:
                    log_entry = log_entry.merge(e)
        log_file_path = self._path_to_log_file(log_directory, log_filename)
        ts = _logfile_state.get_section("timestamps").get(log_file_path, 0)
        output_text = list()
        last_t = 0
        for (t, text) in log_entry.get_filtered_entries(ts):
            dt = datetime.datetime.fromtimestamp(t)
            output_text.append("[frame {}/{} (~{}%), timestamp {}]\n{}".format(frame_counter.current_frame + 1,
                                                                               frame_counter.total_frames,
                                                                               round(frame_counter.progress * 100),
                                                                               dt.strftime(self._get_tm_format(
                                                                                   clock_has_24_hours)), text.rstrip()))
            output_text.append("---")
            last_t = max(t, last_t)
        output_text = "\n".join(output_text) + "\n"
        if stdout:
            print(output_text)
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(output_text)
        _logfile_state.get_section("timestamps").update(log_file_path, 0, lambda _: last_t)
        return ()


def _align_num(n: int, alignment: int, type: str):
    if alignment <= 1:
        return n
    if type == "ceil":
        return int(math.ceil(float(n) / alignment)) * alignment
    elif type == "floor":
        return int(math.floor(float(n) / alignment)) * alignment
    else:
        return int(round(float(n) / alignment)) * alignment


class DreamFrameDimensions:
    NODE_NAME = "Common Frame Dimensions"
    ICON = "⌗"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "size": (["3840", "1920", "1440", "1280", "768", "720", "640", "512"],),
                "aspect_ratio": (["16:9", "16:10", "4:3", "1:1", "5:4", "3:2", "21:9", "14:9"],),
                "orientation": (["wide", "tall"],),
                "divisor": (["8", "4", "2", "1"],),
                "alignment": ("INT", {"default": 64, "min": 1, "max": 512}),
                "alignment_type": (["ceil", "floor", "nearest"],),
            },
        }

    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("INT", "INT", "INT", "INT")
    RETURN_NAMES = ("width", "height", "final_width", "final_height")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def result(self, size, aspect_ratio, orientation, divisor, alignment, alignment_type):
        ratio = tuple(map(int, aspect_ratio.split(":")))
        final_width = int(size)
        final_height = int(round((float(final_width) * ratio[1]) / ratio[0]))
        width = _align_num(int(round(final_width / float(divisor))), alignment, alignment_type)
        height = _align_num(int(round((float(width) * ratio[1]) / ratio[0])), alignment, alignment_type)
        if orientation == "wide":
            return (width, height, final_width, final_height)
        else:
            return (height, width, final_height, final_width)
