# -*- coding: utf-8 -*-
import sys, os

sys.path.append(str(os.path.dirname(os.path.abspath(__file__))))

from . import shared


def setup_default_config():
    shared.DreamConfig()


def run_install():
    setup_default_config()


if __name__ == "__main__":
    run_install()
