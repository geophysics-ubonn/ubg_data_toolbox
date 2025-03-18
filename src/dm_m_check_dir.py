#!/usr/bin/env python
"""Check a single measurement directory (m_*)
"""
import os
import sys
import configparser

from prompt_toolkit.shortcuts import button_dialog

import ubg_data_toolbox.dirtree_nav as dirtree_nav
from ubg_data_toolbox.dir_levels import measurement_lab, measurement_field
from ubg_data_toolbox import id_handling

nodes = {
    'field': measurement_field,
    'laboratory': measurement_lab,
}


class colors:
    """
    Usage:

        print(colors.RES + 'STRING' + colors.ENDC)

    """
    RED = '\033[31m'
    ENDC = '\033[m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'


def main():
    # get the directory to work on
    if len(sys.argv) == 2:
        directory = sys.argv[1]
        assert os.path.isdir(directory), 'Argument is not a valid directory'
    else:
        # assume pwd as directory
        directory = os.getcwd()

    print('Working in directory', directory)
    id_handler = id_handling.data_id_handler(
        directory,
        try_cache=True,
        update_cache=False,
    )

    # check if we already are located within a data directory. This can fail,
    # but if we get a valid data directory, then we can try to infer the
    # survey_type and select the correct checks
    presets = dirtree_nav.get_dirtree_values(directory)

    node = None
    if presets.get('t', None) is not None:
        node = nodes.get(presets['t'], None)

    if node is None:
        # we failed to determine the survey type, not check if there is a
        # metadata.ini file
        mfile = directory + os.sep + 'metadata.ini'
        if os.path.isfile(mfile):
            config = configparser.ConfigParser()
            config.read(mfile)
            if config['general'].get('survey_type', None) is not None:
                node = nodes.get(config['general'].get('survey_type'), None)

    if node is None:
        # last resort, ask the user
        pass
        print('ASKING USER')

        result = button_dialog(
            title='Select survey type',
            text='What type of measurement is this?',
            buttons=[
                ('Field', 'field'),
                ('Laboratory', 'laboratory'),
                ('No idea', None)
            ],
        ).run()
        if result in ('field', 'laboratory'):
            node = nodes.get(result)

    if node is None:
        print('-' * 80)
        print('WARNING:')
        print('We need to know if this is a laboratory or field measurement')
        print('quitting for now')
        print('-' * 80)

    for key, item in node.checks.items():
        print('# CHECK:', key)
        check_value, error_msg = item(directory, id_handler)
        if check_value == 0:
            print(colors.GREEN, end='')
        elif check_value == 1:
            print(colors.YELLOW, end='')
        elif check_value == 2:
            print(colors.RED, end='')

        print(error_msg.replace('\n', '\n' + '    '), end='')
        print(colors.ENDC)

        print('')
