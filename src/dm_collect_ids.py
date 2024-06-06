#!/usr/bin/env python
"""
Collect all existing IDs from the current data directory. Store result in the
file dm_ids.info

"""
import json
import os

from ubg_data_toolbox.dirtree_nav import find_data_root
from ubg_data_toolbox.metadata import metadata_chain


def get_all_measurement_directories(directory):
    """For the given directory, find the data root directory and then return a
    list of all valid measurement directories (i.e., those m_* directories with
    a metadata.ini file)

    Parameters
    ----------
    directory : str
        Directory from which to start looking for the data root

    Returns
    -------
    m_dirs : list
        List of full paths to measurement directories
    """
    dr_root = find_data_root(directory)
    assert dr_root is not None, 'Could not find a data root directory'
    pwd = os.getcwd()
    print('Changing work directory to', dr_root)
    os.chdir(dr_root)

    m_dirs = []
    for root, dirs, files in os.walk('.'):
        if os.path.basename(root).startswith('m_'):
            metadata_file = root + os.sep + 'metadata.ini'
            if os.path.isfile(metadata_file):
                # print(root)
                m_dirs.append(os.path.abspath(root))

    os.chdir(pwd)
    return m_dirs


def main():
    m_dirs = get_all_measurement_directories(os.getcwd())

    data_root = find_data_root(os.getcwd())

    # contains path: id pairs (paths relative to data root)
    id_dict = {}

    for mdir in m_dirs:
        chain = metadata_chain(mdir)
        data = chain.get_merged_metadata()
        if 'id' in data['general']:
            relpath = os.path.relpath(
                mdir,
                start=data_root
            )
            id_dict[relpath] = data['general']['id'].value

    print('Found ids:')
    print(id_dict)
    outfile = data_root + os.sep + 'dm_ids.json'
    print('Saving to:', outfile)
    with open(outfile, 'w') as fid:
        json.dump(id_dict, fid)


if __name__ == '__main__':
    main()
