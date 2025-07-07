"""
Handle meta data
"""
import os
import configparser

from ubg_data_toolbox.metadata_definitions import get_md_values
from ubg_data_toolbox.metadata_definitions import md_entry
from ubg_data_toolbox.dirtree_nav import find_data_root


def _get_configparser():
    return configparser.ConfigParser(
        comment_prefixes=None,
        interpolation=None,
    )


def merge_md_dicts(md1, md2):
    """
    Merge two md_dicts by copying all entries from md2 into md1

    Return md1
    """
    if md2 is None:
        return md1
    for section in md2.keys():
        if section not in md1:
            md1[section] = {}
        for name, item in md2[section].items():
            md1[section][name] = item
    return md1


def write_md_nested_dict_to_file(md_entries, filename):
    """
    Given a nested dict of metadata objects (from
    .metadata_definitions.get_md_values), generate a metadata.ini file

    Parameters
    ----------

    """
    cfg_file = _get_configparser()
    for section in md_entries.keys():
        cfg_file.add_section(section)
        for key in md_entries[section].keys():
            value = md_entries[section][key].value
            if value is not None:
                cfg_file[section][key] = value
    with open(filename, 'w') as fid:
        cfg_file.write(fid)


def gen_paths(full_dir):
    directory = full_dir
    yield directory
    counter = 20
    while counter > 0 and os.path.basename(directory).split('_')[0] != 'dr':
        directory = os.path.dirname(directory)
        yield directory
        counter -= 1


class metadata_chain(object):
    """Handle a chain of metadata files. Starting from a provided (lowest)
    directory or metadata.ini file, find all metadata.ini files in higher
    directories up to the data root.
    Then, work with the data. Planned features:

        * return a unified metadata object containing all data from all files
        * identify duplicate entries
        * identify duplicate and differing entries
    """
    def __init__(self, entry_path_or_file):
        """
        Parameters
        ----------
        entry_path_or_file : str
            Directory or path to metadata.ini filename
        """
        entry_path_or_file = os.path.abspath(entry_path_or_file)
        if os.path.isfile(entry_path_or_file):
            self.directory = os.path.dirname(entry_path_or_file)
            filename = os.path.basename(entry_path_or_file)
            assert filename == 'metadata.ini'
        else:
            self.directory = entry_path_or_file

    def get_available_metadata_files(self):
        fragments = gen_paths(self.directory)
        md_files = []
        for subdir in fragments:
            filename = subdir + os.sep + 'metadata.ini'
            if os.path.isfile(filename):
                md_files.append(filename)
        return md_files

    def get_merged_metadata(self):
        filenames = self.get_available_metadata_files()
        config_raw = self._import_metadata_files(filenames)
        metadata_tree = self._import_metadata_files_to_md_dict(config_raw)
        return metadata_tree

    def _import_metadata_files(self, filenames=None, debug=False):
        """merge the metafiles provided in filenames.

        The files are read in increasing order, that is, later filenames will
        overwrite duplicate entries from previous files.

        Parameters
        ----------
        filenames : tuple|list|None
            Filenames to import. If None, then search for all metadata.ini
            files along the path tree using self.get_available_metadata_files
        """
        if filenames is None:
            filenames = self.get_available_metadata_files()
        config = _get_configparser()

        # read in config files
        for filename in filenames:
            dataroot = find_data_root(os.path.dirname(filename))
            if debug:
                print(
                    'Loading filename',
                    os.path.relpath(filename, os.path.dirname(dataroot))
                )
            config.read(str(filename))

        return config

    def _import_metadata_files_to_md_dict(
            self, cfg_input, ignore_sections=None):
        """
        Parameters
        ----------
        cfg_input : configparser.ConfigParser


        """
        if isinstance(cfg_input, configparser.ConfigParser):
            metadata_raw = cfg_input
        else:
            # assume a list of filenames
            metadata_raw = self.import_metadata_files(cfg_input)
        md_dict = get_md_values()
        for section in metadata_raw.keys():
            if section == 'DEFAULT':
                # for now we only work with sections
                continue
            if ignore_sections is not None and section in ignore_sections:
                continue
            if section not in md_dict:
                md_dict[section] = {}
            for name, value in metadata_raw[section].items():
                if name in md_dict[section]:
                    md_dict[section][name].value = value
                else:
                    new_entry = md_entry(
                        name=name,
                        value=value,
                        is_extra=True,
                    )
                    md_dict[section][name] = new_entry
        return md_dict


class metadata_manager(object):
    """Manage metadata contained in a proper directory structure of datasets.

    WARNING: This is an class originating in the early development states of
    the data_toolbox. It is possibly not of much use.
    """

    def __init__(self, path_raw):
        """

        Parameters
        ----------
        path_raw : str
            The path that we are working on. Can be an absolute path with
            non-database parts.
        """
        self.path_raw = path_raw

    def find_metadata_files(self):
        """
        Return the absolute paths of all metadata.ini files in the dirtree
        """
        metadata_files = []
        for root, dirs, files in os.walk(self.path_raw):
            if 'metadata.ini' in files:
                metadata_files.append(
                    os.path.abspath(root + os.sep + 'metadata.ini')
                )
        return metadata_files

    def import_metadata_files(self, filenames):
        """merge the metafiles provided in filenames.

        The files are read in increasing order, that is, later filenames will
        overwrite duplicate entries from previous files.
        """
        config = _get_configparser()

        # read in config files
        for filename in filenames:
            config.read(str(filename))

        return config

    def import_metadata_files_to_md_dict(
            self, cfg_input, ignore_sections=None):
        """
        Parameters
        ----------
        cfg_input : configparser.ConfigParser

        """
        if isinstance(cfg_input, configparser.ConfigParser):
            metadata_raw = cfg_input
        else:
            # assume a list of filenames
            metadata_raw = self.import_metadata_files(cfg_input)
        md_dict = get_md_values()
        for section in metadata_raw.keys():
            if section == 'DEFAULT':
                # for now we only work with sections
                continue
            if ignore_sections is not None and section in ignore_sections:
                continue
            if section not in md_dict:
                md_dict[section] = {}
            for name, value in metadata_raw[section].items():
                if name in md_dict[section]:
                    md_dict[section][name].value = value
                else:
                    new_entry = md_entry(
                        name=name,
                        value=value,
                        is_extra=True,
                    )
                    md_dict[section][name] = new_entry
        return md_dict
    # #########################################################################
    # Eveything down below is old and needs to be reviewed !!!!
    # #########################################################################

    # Part of __init__
        # # store metadata paths. This is used for caching purposes
        # # storing pattern: path: [True|False]
        # # True: contains metadata.ini file
        # self.md_paths = {}

        # self.all_metadata_entries = {}
        # self.all_metadata_entries['general'] = [
        #     'id',
        #     'date',
        #     'time',
        #     'person_responsible',
        #     'person_email',
        #     'attending_persons',
        #     'site',
        #     'area',
        #     'profile',
        #     'measurement_type',
        #     'keywords',
        #     'description_short',
        #     'description',
        #     'description_exp',
        #     'survey_type',
        #     'related_dois',
        #     'analysis_links',
        #     'problems',
        #     'missing',
        #     'restrictions',
        #     'signed_off_by',
        # ]

    def get_data_levels(self):
        """Using the raw data path, determine the data levels

        Returns
        -------
        dlevels : list of strings
        """
        from pathlib import Path
        x = Path(self.path_raw)
        for nr in reversed(range(0, len(x.parts))):
            if x.parts[nr].startswith('rd_'):
                break
        self.dlevels = x.parts[nr:]
        return self.dlevels

    @staticmethod
    def find_all_datasets(directory):
        """Find and return all datasets in a given directory.

        Datasets are characterized by the following criteria:

            * metadata.ini file
            * subdirectories: RawData, DataProcessed(opt), Analysis (opt)

        Criteria marked with (opt) are optional and can be created when needed

        Returns
        -------
        directory : list of dataset directories
        """
        dataset_directories = []
        for root, dirs, files in os.walk(directory):
            # check if this directory is a dataset directory
            if 'metadata.ini' in files and 'DataRaw' in dirs:
                dataset_directories.append(root)

        return dataset_directories

    @staticmethod
    def return_metadata_file(dataset_dir):
        """Return all metadata files along a given directory path. Cache all
        metadata files found. Sort with ascending priority, that is, from top
        to bottom. The metadata.ini file residing in the measurement directory
        has the highest priority, and overwrites everything else.
        """
        metafiles = []
        path = ''
        for directory in dataset_dir.split('/'):
            path += directory + os.sep
            mfile = path + 'metadata.ini'
            if os.path.isfile(mfile):
                metafiles.append(mfile)
        return metafiles

    def import_metafile(self, filename):
        config = _get_configparser()
        if filename is not None:
            config.read(str(filename))
        return config


if __name__ == '__main__':
    datasets = metadata_manager.find_all_datasets('../Examples')
    print('datasets', datasets)

    md_manager = metadata_manager()
    md_manager.return_metadata_file(datasets[0])
    md_manager = metadata_manager()

    config = md_manager.merge_metafile(
        ['config1.ini', 'config2.ini', 'config3.ini']
    )

    with open('config_merge.ini', 'w') as fid:
        config.write(fid)
