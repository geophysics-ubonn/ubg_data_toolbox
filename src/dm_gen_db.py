#!/usr/bin/env python
"""
Generate a pandas dataframe with all metadata included.

WARNING: This is the really dumb way and I'm not sure this scales. However, I
hope for now it is enough.

Todo: custom metadata entries are not imported at the moment

"""
import os

import pandas as pd

from ubg_data_toolbox.dirtree_nav import find_data_root
from ubg_data_toolbox.metadata import metadata_chain


def main():
    dr_root = find_data_root(os.getcwd())
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
                m_dirs.append(root)

    global_df_list = []

    for mdir in m_dirs:
        print(mdir)
        chain = metadata_chain(mdir)
        data = chain.get_merged_metadata()
        assert 'id' in data['general'], 'ID required for processing'
        df_list = []
        for section in data:
            subdata = data[section]
            subdf = pd.DataFrame(
                {x[1].name: x[1].value for x in subdata.items()},
                index=[data['general']['id'].value, ])
            subdf.columns = pd.MultiIndex.from_product(
                [[section, ], list(subdf.columns)])
            df_list.append(subdf)
        df = pd.concat(df_list, axis=1)
        global_df_list.append(df)

    df_all = pd.concat(global_df_list)
    os.makedirs('.management', exist_ok=True)
    filename = '.management/db.pickle'
    print('Writing database file to', filename)
    df_all.to_pickle(filename)
    os.chdir(pwd)


if __name__ == '__main__':
    main()
