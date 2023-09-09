# -*- coding: utf-8 -*-
def _get_node_name(cls):
    return cls.__dict__.get("NODE_NAME", str(cls))


def on_error(node_cls: type, message: str):
    msg = "Failure in [" + _get_node_name(node_cls) + "]:" + message
    print(msg)
    raise Exception(msg)
