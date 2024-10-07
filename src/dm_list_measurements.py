#!/usr/bin/env python
"""List all measurements
"""

import os
import argparse

from ubg_data_toolbox.dirtree import tree
from ubg_data_toolbox.dirtree_nav import find_data_root
from ubg_data_toolbox.metadata import metadata_chain


def handle_args():
    parser = argparse.ArgumentParser(
        description='Add one measurement to a given data directory structure',
    )
    parser.add_argument(
        '-g', '--general',
        help='Also print out metadata from [general] (separate keys with ;)',
        required=False,
    )
    args = parser.parse_args()
    return args


def _get_prefix(directory):
    workstr = os.path.basename(os.path.abspath(directory))
    assert isinstance(directory, str)
    if workstr.find('_') == -1:
        return None
    return workstr.split('_')[0]


def _get_directory_name(directory):
    """Return the name of the directory by removing the prefix.
    Return None if no prefix was found
    """
    workstr = os.path.basename(os.path.abspath(directory))
    assert isinstance(directory, str)
    if workstr.find('_') == -1:
        return None
    return workstr.split('_')[1]


def walk_and_print_dirtree(
        directory, nodes, basedir, level=0, metadata_entries=None):
    dr_root = find_data_root(directory)
    directory_name = os.path.basename(os.path.abspath(directory))
    # print('@@@')
    # print(directory)
    # print(dr_root)
    # relpath = os.path.relpath(directory, os.path.dirname(dr_root))

    # the nodes list contains all dir levels allowed for this level
    # print('    ' * level + 'Directory', relpath)

    # print(
    #     '    ' * level + 'Corresponding tree entry',
    #     [node.name for node in nodes])

    # We allow some directories that can contain arbitrary information.
    # Don't test them
    passive_directories = [
        'Documentation',
    ]
    if directory_name in passive_directories:
        return

    # We also ignore .* directories - these are only used for temporary data
    if directory_name.startswith('.'):
        # print(
        #     '    ' * (level + 1) +
        #     "Directory starts with a dot, will not be analysed"
        # )
        return

    # Go through all possible nodes and check if one fits
    found_a_prefix = False
    node = None
    for test_node in nodes:
        # check prefix
        prefix = _get_prefix(directory)
        check_prefix = test_node.abbreviation == prefix
        # print('    ' * level + 'check_prefix', check_prefix)
        if check_prefix:
            found_a_prefix = True
            # this is the node corresponding to this directory level here
            node = test_node
    if not found_a_prefix:
        return
    # print(node.name, node.abbreviation, node)
    # TODO: Any level-specific tests could now be called here using the node
    # variable, which could also directly store these tests.

    if prefix == 'm':
        # found one measurement
        print(
            os.path.relpath(
                directory,
                os.path.dirname(dr_root)
            )
        )

        if metadata_entries is not None:
            chain = metadata_chain(directory)
            mdata = chain.get_merged_metadata()
            items = metadata_entries.split(';')
            if 'general' in mdata:
                for item in items:
                    if item in mdata['general']:
                        print(' ' * 8 + '{} = {}'.format(
                            item,
                            mdata['general'][item].value
                        ))

    # Next level:
    subdirs = [
        os.path.normpath(
            directory + os.sep + x
        ) for x in sorted(
            os.listdir(directory)) if os.path.isdir(directory + os.sep + x)]
    # print('   ' * level + 'subdirs', subdirs)

    # we ignore "normal" children in case of conditional children
    if len(node.conditional_children) > 0:
        name = _get_directory_name(directory)
        if name not in node.conditional_children:
            print(
                'ERROR: This node has the value: "{}".'.format(name) +
                ' However, we only allowed those values {}'.format(
                    node.conditional_children.keys()
                )
            )
            return
        else:
            child_nodes = [node.conditional_children[name], ]
            for subdir in subdirs:
                # found a condition
                walk_and_print_dirtree(
                    subdir, child_nodes, basedir, level + 1,
                    metadata_entries
                )
    else:
        # do not continue of there are no remaining node children
        if len(node.children) == 0:
            return

        for subdir in subdirs:
            walk_and_print_dirtree(
                subdir, node.children, basedir, level + 1, metadata_entries
            )


def main():
    args = handle_args()

    directory = os.getcwd()
    dr_root = find_data_root(directory)
    print(
        'Measurement directories found in data root: {}'.format(
            dr_root
        )
    )
    print('.' * 80)
    assert dr_root is not None, 'cannot find dr data root, must begin with dr_'
    walk_and_print_dirtree(
        dr_root,
        [tree, ],
        basedir=os.getcwd(),
        # basedir=dr_root,
        level=0,
        metadata_entries=args.general,
    )
    print('.' * 80)
