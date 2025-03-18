#!/usr/bin/env python
"""

"""
import logging
import os
import argparse

from ubg_data_toolbox.dirtree_nav import find_data_root
# from ubg_data_toolbox.metadata import metadata_chain
from ubg_data_toolbox.id_handling import data_id_handler


def handle_args():
    parser = argparse.ArgumentParser(
        description='Update the ID map found in .management/id_maps.cache',
    )
    parser.add_argument(
        '-t', '--tree',
        help='Path of data tree (should start with: dr_). If not given, ' +
        'use PWD ',
        required=False,
    )
    parser.add_argument(
        '-l', '--level',
        help='Level to start checking on. This is a directory that MUST ' +
        'reside within the data root indicated by -t/--tree',
        required=False,
    )

    parser.add_argument(
        '--debug', help='Debug output', required=False,
        action='store_true',
    )
    args = parser.parse_args()
    return args


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

    if args.tree is None:
        # assume pwd as directory
        directory = os.getcwd()
    else:
        directory = args.tree
        assert os.path.isdir(directory), 'Argument is not a valid directory'

    logger.debug('Working in directory', directory)
    dr_root = find_data_root(directory)
    assert dr_root is not None, 'cannot find dr data root, must begin with dr_'

    logger.info('Initializing data id handler')
    id_handler = data_id_handler(
        datatree=dr_root,
        try_cache=True,
        update_cache=False,
        loglevel=loglevel,
    )
    id_handler
    id_handler.update_id_maps_from_dirtree(subdir=args.level)
    id_handler.save_to_cache()
    # import IPython
    # IPython.embed()
