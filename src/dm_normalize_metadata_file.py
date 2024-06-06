#!/usr/bin/env python
"""
Normalize a metadata.ini file in the present directory.

"""
import os

from ubg_data_toolbox.metadata import metadata_chain


def main():
    if os.path.isfile('metadata.ini'):
        mdir = os.getcwd()
        chain = metadata_chain(mdir)
        config = chain._import_metadata_files()
        with open('metadata.ini' + '.norm', 'w') as fid:
            config.write(fid)


if __name__ == '__main__':
    main()
