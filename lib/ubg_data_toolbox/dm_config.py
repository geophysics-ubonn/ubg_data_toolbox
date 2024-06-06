""" Manage configuration options for the data toolbox

Configuration files commonly have the name "ub_geoph_dm.cfg"
We support local and global configuration files:

    * in present working directory
    * in home directory

"""
import os
import configparser

from ubg_data_toolbox.metadata import metadata_manager


def parse_config_file(filename):
    """
    Parse a given configuration file
    """
    config = configparser.ConfigParser()
    config.read(str(filename))
    return config


def find_config_highest_priority(user_override=None):
    """
    Look in the predefined locations for configuration files. Stop as soon as a
    filename is found.

    Parameters
    ----------
    user_override : str (optional)
        If given, treat this as a user-supplied configuration path file and
        append to the list of possible locations as highest priority

    Returns
    -------

    """
    name_of_config = 'ub_geoph_dm.cfg'
    # locations in increasing priority
    locations = [
        os.environ[
            'HOME'] + os.sep + '.data_toolbox' + os.sep + name_of_config,
        os.getcwd() + os.sep + name_of_config,
    ]
    if user_override is not None:
        locations.append(user_override)

    for filename in reversed(locations):
        if os.path.isfile(filename):
            return os.path.abspath(filename)


def create_new_config_file(directory):
    filename = directory + os.sep + 'ub_geoph_dm.cfg'
    assert not os.path.isfile(filename), 'Config file already exists'
    os.makedirs(directory, exist_ok=True)
    config = configparser.ConfigParser()
    config['settings'] = {
        'input_default_values': os.path.abspath(
            directory
        ) + os.sep + 'cache_metadata.cache',
    }
    with open(filename, 'w') as fid:
        config.write(fid)
    return filename


def get_configuration(get_default_metadata=False, create_if_required=False):
    """Return the configuration of the dm_toolbox.

    The configuration settings are stored in the "settings" section of the
    configuration ini file.

    Try different locations for the configuration file.

    Parameters
    ----------
    get_default_metadata : bool, optional
        If True, also import metadata from config files. This basically imports
        the config file into a configparser object and ignores the "settings"
        section
    create_if_required : bool, optional
        If True, create a configuration file in
        $HOME/.data_toolbox/ub_geoph_dm.cfg for further use

    """
    filename = find_config_highest_priority()
    if filename is None and create_if_required:
        directory = os.environ['HOME'] + os.sep + '.data_toolbox'
        filename = create_new_config_file(directory)

    print('Filename with highest priority', filename)
    if filename is not None and os.path.isfile(filename):
        config_raw = parse_config_file(filename)
        # split into the settings and the metadata presets
        config = config_raw['settings']
        # import IPython
        # IPython.embed()
        if get_default_metadata:
            mgr = metadata_manager(None)
            metadata = mgr.import_metadata_files_to_md_dict(
                config_raw,
                ignore_sections=['settings', ]
            )
    else:
        # we did not find a suitable configuration file
        config = None
        metadata = None

    if get_default_metadata:
        return config, metadata
    return config
