#!/usr/bin/env python
"""dm_gen_zip - Generate a zip file of a data tree for easy transfer

"""
import logging
import os
import pathlib
import shutil
import argparse

from ubg_data_toolbox.dirtree_nav import find_data_root


def handle_args():
    parser = argparse.ArgumentParser(
        description='Create a zip file for a data tree',
    )
    parser.add_argument(
        '-t', '--tree',
        help='Path of data tree (should start with: dr_). If not given, ' +
        'use PWD ',
        required=False,
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file. if not given, ".zip" will be appended at the end.',
        required=True,
    )
    parser.add_argument(
        '--debug', help='Debug output', required=False,
        action='store_true',
    )
    args = parser.parse_args()

    # check for .zip ending
    if args.output.endswith('.zip'):
        # strip .zip - will be added automatically later
        args.output = args.output[:-4]

    return args


def gen_zip(dr_tree_dir, output):
    """Generate the actual zip file

    Parameters
    ----------
    dr_tree_dir : str
        The path to a data tree. This can also point to a subdirectory of the
        tree. However, always the complete tree is archived.
    output : str
        The output file path. Can be relative to PWD

    """
    dr_root = find_data_root(dr_tree_dir)
    assert dr_root is not None, 'cannot find dr data root, must begin with dr_'

    if os.path.isfile(output):
        print('WARNING: Output file {} already exists. Stopping here'.format(
            output
        ))

    output_abs = os.path.abspath(output)

    pwd = pathlib.Path(os.getcwd())

    os.chdir(pathlib.Path(os.path.abspath(dr_root)).parent)

    shutil.make_archive(
        output_abs,
        'zip',
        os.path.basename(dr_tree_dir),
        base_dir=os.path.relpath(
            os.path.abspath(dr_root),
            start=os.path.basename(dr_root)
        )
    )
    os.chdir(pwd)


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
    logger.info(
        "Generating zip file {} for data tree: {}".format(
            args.output,
            args.tree,
        )
    )
    gen_zip(args.tree, args.output)
