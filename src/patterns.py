#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Error pattern replacements"""


CORONAL_BACKING = {
    "t": "k",
    "d": "g",
    "n": "N"  # ?
}


R_WEAKENING = {
    "r": "j"
}


STOPPING = {
    "C": "t",
    "f": "p",
    "v": "b",
    "s": "t",
    "s`": "t`",
    "s'": "t",
    "x\\": "k",
    "S": "t",
    "tS": "t",
    "z": "d",
    "Z": "d",
    "dZ": "d",
    "T": "t",  # or ->p
    "D": "d",  # or ->b
}


VELAR_FRONTING = {
    "k": "t",
    "g": "d",
    "N": "n"
}
