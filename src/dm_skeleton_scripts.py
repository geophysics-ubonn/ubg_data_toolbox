#!/usr/bin/env python
"""Given a location of a measurement (m_*) directory, update the metadata.ini
file with all metadata that can be extracted from the directory path

"""
import os

import logging
import argparse


def handle_args():
    parser = argparse.ArgumentParser(
        description='Update the ID map found in .management/id_maps.cache',
    )
    parser.add_argument(
        '-m',
        '--mdir',
        help='Path to m_ directory',
        required=False,
    )
    # parser.add_argument(
    #     '-l', '--level',
    #     help='Level to start checking on. This is a directory that MUST ' +
    #     'reside within the data root indicated by -t/--tree',
    #     required=False,
    # )

    parser.add_argument(
        '--debug', help='Debug output', required=False,
        action='store_true',
    )
    args = parser.parse_args()
    return args


class update_md_from_path(object):
    def __init__(self, path, loglevel):
        self.path = path
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(loglevel)


def main():
    logging.basicConfig(
        level=logging.INFO
    )
    args = handle_args()
    if args.debug:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO
    logger = logging.getLogger(__name__)
    logger.setLevel(loglevel)

    if args.mdir is not None:
        mdir = args.mdir
    else:
        mdir = os.getcwd()

    assert os.path.isdir(mdir), "Directory {} must exist!".format(mdir)
    assert os.path.basename(mdir).startswith('m_'), "This is not a m_ dir!"

    updater = update_md_from_path(mdir, loglevel)
