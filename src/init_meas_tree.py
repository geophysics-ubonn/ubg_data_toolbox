#!/usr/bin/env python3
# *-* coding: utf-8 *-*
""" Initialize a measurement directory tree """
import os


if __name__ == '__main__':
    directories = (
        'DataRaw',
        'DataProcessed',
        'Analysis',
        'Pictures',
        'Documentation',
    )
    for directory in directories:
        if not os.path.isdir(directory):
            os.makedirs(directory)
