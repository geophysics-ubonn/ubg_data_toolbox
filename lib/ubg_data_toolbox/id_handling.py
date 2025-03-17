"""Various functionality for handling measurement ids

"""
import logging
import os
import json
import pathlib

from ubg_data_toolbox.dirtree_nav import find_data_root
from ubg_data_toolbox.metadata import metadata_chain


class data_id_handler(object):
    """Work with IDs in a data tree"""

    def __init__(self, datatree, try_cache=False, update_cache=False,
                 loglevel=logging.INFO):
        """
        Parameters
        ----------
        datatree: str
            Path to data tree. This can also be a subdirectory of the tree -
            the data root is then found automatically
        try_cache: bool, default: False
            If True, try to load id maps from the cache. If the cache is
            present, do not attempt to rescan the directory tree
        update_cache: bool, default: False
            If True, then update the cache of the complete data tree
        loglevel: valid log-level of the logging module
            Defaults to logging.INFO

        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(loglevel)
        self.logger.debug('Initializing ID handler')
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
            self.logger.debug('trying cache for existing id map')
            if not self.load_from_cache():
                self.logger.debug('cache file not found')
                if update_cache:
                    self.logger.debug('updating id map from tree')
                    # cache was not found
                    self.update_id_maps_from_dirtree()
                else:
                    self.logger.debug('will not update tree')

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

    def update_id_maps_from_dirtree(self, subdir=None):
        """Scan the complete tree and update the id maps

        Parameters
        ----------
        subdir : None|str
            If provided with a valid path, use this path as the starting point
            of the search

        """
        if subdir is not None:
            start_dir = os.path.abspath(subdir)
        else:
            start_dir = self.dr_root

        print('inside id handler')
        # import IPython
        # IPython.embed()

        assert os.path.isdir(start_dir), '{} directory must exist'.format(
            start_dir)

        p_start = pathlib.Path(start_dir)
        p_dr = pathlib.Path(self.dr_root)
        if p_start != p_dr and p_dr not in p_start.parents:
            raise Exception('The subdir must be located in the data root')

        # check if path inside our data root

        pwd = os.getcwd()
        os.chdir(self.dr_root)
        start_dir_rel = os.path.relpath(start_dir, start=self.dr_root)
        self.logger.debug(
            'starting to update ids from directory: {}'.format(
                start_dir
            )
        )
        # collect all measurement directories with a metadata.ini file
        m_dirs = []
        for root, dirs, files in os.walk(start_dir_rel):
            if os.path.basename(root).startswith('m_'):
                metadata_file = root + os.sep + 'metadata.ini'
                if os.path.isfile(metadata_file):
                    m_dirs.append(root)

        print(m_dirs)
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

        self.logger.debug('done updating id maps')
        print(self.id2path)

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
