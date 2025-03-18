#!/usr/bin/env python
# *-* coding: utf-8 *-*
"""Initialize a bare minimum configuration file. By default only the keys will
be created, no values will be filled in. This could be added in later versions
of this program.
"""
import os
import configparser
import argparse

from ubg_data_toolbox.metadata import metadata_chain

import ubg_data_toolbox.dm_dirtree as dm_dirtree


def handle_args():
    parser = argparse.ArgumentParser(
        description='Initialize a metadata.ini file',
    )
    parser.add_argument(
        '--overwrite',
        help='Overwrite an existing metadata.ini file',
        required=False,
        action='store_true',
    )

    # parser.add_argument(
    #     '--debug', help='Debug output', required=False,
    #     action='store_true',
    # )
    args = parser.parse_args()
    return args


def init_empty_config():
    """Return a config object with all required keys
    """
    config = configparser.ConfigParser()
    return config


def main():
    args = handle_args()
    if os.path.isfile('metadata.ini') and not args.overwrite:
        print('metadata.ini already exists. Stopping here')
        print('Use the --overwrite switch to overwrite')
        exit()
        # leav this here in case this is executed in ipython
        1 / 0

    mdir = os.getcwd()
    # find all metadata files and merge them
    chain = metadata_chain(mdir)
    metadata = chain.get_merged_metadata()

    metadata = dm_dirtree.gen_metadata_from_mdir('.', metadata)

    print('Content of new metadata.ini:')
    print(metadata)

    print('')
    print('')
    print('')
    print('Writing to metadata.ini')
    print(os.getcwd())
    metadata.to_file('metadata.ini', overwrite=args.overwrite)


if __name__ == '__main__':
    main()
