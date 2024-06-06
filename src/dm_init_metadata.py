#!/usr/bin/env python
# *-* coding: utf-8 *-*
"""Initialize a bare minimum configuration file. By default only the keys will
be created, no values will be filled in. This could be added in later versions
of this program.
"""
import configparser
import os
from collections import OrderedDict

import ubg_data_toolbox.dirtree_nav as dirtree_nav


def init_empty_config():
    """Return a config object with all required keys
    """
    config = configparser.ConfigParser()
    return config


def main():
    config = init_empty_config()

    # try to fill in values based on the directory structure
    presets = {}
    presets = dirtree_nav.get_dirtree_values('.')
    # data_root = dirtree_nav.find_data_root('.')
    # if data_root is not None:
    #     # only try to fill in defaults if we have a valid directory structure
    #     basedir = os.path.dirname(data_root)
    #     # get our directory structure within the data directory
    #     treeitems = os.path.relpath(os.getcwd(), basedir).split('/')
    #     for item in treeitems:
    #         index = item.find('_')
    #         if index > 0:
    #             abbreviation = item[0:index]
    #             value = item[index + 1:]
    #             presets[abbreviation] = value
    #     print(presets)
    # else:
    if len(presets.keys()) == 0:
        print(
            'It seems that we are not located in a proper data directory. ' +
            'No defaults will be filled in.'
        )

    # we want to include those entries, empty or pre-filled, in the metadata
    # file
    # if an entry is a two-entry list, then the second item refers to the
    # prefix of a directory name from which this entry will be pre-filled, if
    # available

    # [general] section
    default_entries_general = [
        ['label', 'm'],
        'person_responsible',
        'person_email',
        'description',
        'datetime_start',
        'description',
        'restrictions',
        'completed',
        ['survey_type', 't'],
        ['theme_complex', 'tc'],
        ['method', 'md'],
    ]

    default_entry_field = [
        ['site', 's'],
        ['area', 'a'],
        ['profile', 'p'],
    ]

    default_entries_lab = [
        ['site', 's'],
    ]

    groups = {
        'general': default_entries_general,
        'field': default_entry_field,
        'laboratory': default_entries_lab,
    }

    # always include the general defaults
    keys = ['general', ]

    # depending on the survey_type, add lab or field defaults
    lab_field = presets.get('t', None)
    if lab_field == 'field':
        keys += ['field']
    elif lab_field == 'laboratory':
        keys += ['laboratory']

    for key in keys:
        entries = groups[key]
        config[key] = OrderedDict()
        # metadata_subgroup = obj[key]
        for entry_raw in entries:
            if type(entry_raw) is list:
                entry = entry_raw[0]
                dir_prefix = entry_raw[1]
            else:
                entry = entry_raw
                dir_prefix = None

            default_value = presets.get(dir_prefix, '')
            config[key][entry] = default_value

    if os.path.isfile('metadata.ini'):
        print('metadata.ini file already exists. Exiting!')
        exit()

    print('Content of new metadata.ini')

    for section in config.sections():
        print('[' + section + ']')
        for name, value in config[section].items():
            print('    ', name, '=', value)

    print('Writing new metadata.ini file')
    with open('metadata.ini', 'w') as fid:
        config.write(fid)


if __name__ == '__main__':
    main()
