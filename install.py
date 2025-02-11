# -*- coding: utf-8 -*-
from . import shared


def setup_default_config():
    shared.DreamConfig()


def run_install():
    setup_default_config()


if __name__ == "__main__":
    run_install()
