class DreamLog:
    def __init__(self, debug_active=False):
        self._debug = debug_active

    def _print(self, text: str, *args, **kwargs):
        if args or kwargs:
            text = text.format(*args, **kwargs)
        print("[DREAM] " + text)

    def error(self, text: str, *args, **kwargs):
        self._print(text, *args, **kwargs)

    def info(self, text: str, *args, **kwargs):
        self._print(text, *args, **kwargs)

    def debug(self, text: str, *args, **kwargs):
        if self._debug:
            self._print(text, *args, **kwargs)
