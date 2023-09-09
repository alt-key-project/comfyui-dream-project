# -*- coding: utf-8 -*-
from .shared import DreamConfig


def setup_default_config():
    DreamConfig()


def run_install():
    setup_default_config()


if __name__ == "__main__":
    run_install()
