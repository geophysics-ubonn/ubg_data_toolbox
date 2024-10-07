"""Various functionality for handling measurement ids

"""
import os
import json

from ubg_data_toolbox.dirtree_nav import find_data_root
from ubg_data_toolbox.metadata import metadata_chain


class data_id_handler(object):
    """Work with IDs in a data tree"""

    def __init__(self, datatree, try_cache=True):
        """
        Parameters
        ----------
        datatree: str
            Path to data tree. This can also be a subdirectory of the tree
        try_cache: bool
            If True, try to load id maps from the cache. If the cache is
            present, do not attempt to rescan the directory tree

        """
        # ids and paths are both unique within the data tree
        # we maintain two dictionaries for look-up in both directions
        # Paths are absolute paths
        self.id2path = {}
        self.path2id = {}

        self.datatree = datatree
        assert os.path.isdir(self.datatree), "datatree is not a directory"
        dr_root = find_data_root(self.datatree)
        assert dr_root is not None, 'Could not find a data root directory'
        self.dr_root = dr_root

        # the management directory
        self.mgt_dir = dr_root + os.sep + '.management'

        if try_cache:
            if not self.load_from_cache():
                # cache was not found
                self.update_id_maps_from_dirtree()
        else:
            self.update_id_maps_from_dirtree()

    def load_from_cache(self):
        """Load id maps from cache.

        Returns
        -------
        cache_found: bool
            True if we found a cache, False if not
        """
        cachefile = self.mgt_dir + os.sep + 'id_maps.cache'
        if os.path.isfile(cachefile):
            with open(cachefile, 'r') as fid:
                id2path, path2id = json.load(fid)
            assert isinstance(id2path, dict), "loaded data is not a dict"
            assert isinstance(path2id, dict), "loaded data is not a dict"
            self.id2path = id2path
            self.path2id = path2id
            return True
        return False

    def save_to_cache(self):
        """Save id maps into a json file in the .management subdirectory of the
        dr_ directory level

        """
        if not os.path.isdir(self.mgt_dir):
            os.makedirs(self.mgt_dir)

        outfile = self.mgt_dir + os.sep + 'id_maps.cache'
        with open(outfile, 'w') as fid:
            json.dump([self.id2path, self.path2id], fid)
            return True
        return False

        # import IPython
        # IPython.embed()

    def update_id_maps_from_dirtree(self):
        """Scan the complete tree and update the id maps

        """
        pwd = os.getcwd()
        os.chdir(self.dr_root)

        # collect all measurement directories with a metadata.ini file
        m_dirs = []
        for root, dirs, files in os.walk('.'):
            if os.path.basename(root).startswith('m_'):
                metadata_file = root + os.sep + 'metadata.ini'
                if os.path.isfile(metadata_file):
                    m_dirs.append(root)

        # extract ids
        sub_id2path = {}
        sub_path2id = {}

        for mdir in m_dirs:
            chain = metadata_chain(mdir)
            data = chain.get_merged_metadata()
            if 'id' not in data['general']:
                # we are not interested in measurements with id
                continue
            m_id = data['general']['id'].value
            m_path = os.path.abspath(mdir)

            assert m_id not in sub_id2path, \
                "IDs must be unique in a data directory tree!"
            sub_id2path[m_id] = m_path

            assert m_path not in sub_path2id, \
                "Paths must be unique in a data directory tree!"
            sub_path2id[m_path] = m_id

        # now replace the global maps
        self.id2path = sub_id2path
        self.path2id = sub_path2id

        os.chdir(pwd)

    def check_id_present(self, test_id, update_tree=False):
        """Check if a given id is present in the tree

        Parameters
        ----------
        test_id: str
            The id to check
        update_tree: bool
            If True, rescan the complete directory tree and update the id maps

        Returns
        -------
        id_is_present: bool
            If True, then the id is already present in the directory tree
        """
        if update_tree:
            self.update_id_maps_from_dirtree()
        if test_id in self.id2path:
            return True
        return False
