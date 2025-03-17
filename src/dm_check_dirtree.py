#!/usr/bin/env python
"""Check a data tree for consistency

TODOS:

    * restructure to be used programatically. It would be nice to get defined
    return values so we can easily check if a directory tree is consistent.

"""
import os
import argparse
from pathlib import Path

from ubg_data_toolbox.dirtree import tree
from ubg_data_toolbox import id_handling
from ubg_data_toolbox.dirtree_nav import find_data_root


def handle_args():
    parser = argparse.ArgumentParser(
        description='Add one measurement to a given data directory structure',
    )
    parser.add_argument(
        '-t', '--tree',
        help='Path of data tree (should start with: dr_). If not given, ' +
        'use PWD ',
        required=False,
    )
    parser.add_argument(
        '-l', '--level',
        help='Level to start checking on. This is a directory that MUST ' +
        'reside within the data root indicated by -t/--tree',
        required=False,
    )
    args = parser.parse_args()
    return args


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


def _get_prefix_and_name(directory):
    """Return prefix and name of a given directory

    Returns
    -------
    prefix: str
        Prefix of the directory level
    name: str
        Name of the directory level, separated using '_' by the name

    """
    workstr = os.path.basename(os.path.abspath(directory))
    assert isinstance(directory, str)
    index = workstr.find('_')
    if index == -1:
        return None

    prefix = workstr.split('_')[0]
    name = workstr[index + 1:]
    return prefix, name


def _get_starting_node(start_level_raw, tree, dr_root):
    """

    Parameters
    ----------
    start_level_raw: str
        The path of the starting level directory that we want to get a
        corresponding tree node for
    tree: ?
        The complete directory tree structure that is used for the node search
    dr_root: str
        Path to the top level directory of the data tree (dr_*-directory)

    Returns
    -------
    starting_level: str
        Sanitized version of input start_level_raw
    node: ?| None
        The node corresponding to the starting_level directory path

    """
    levels_to_match = os.path.relpath(start_level_raw, dr_root).split(os.sep)
    node = tree

    # assume no conditional value on first level!
    last_value = None
    for level_dir in levels_to_match:
        # print('----------------------------')
        # print(level_dir, 'last value:', last_value)
        prefix, value = _get_prefix_and_name(level_dir)
        # print('  prefix', prefix, ' value:', value)
        new_node = None
        for child in node.children:
            # print(child)
            if child.abbreviation == prefix:
                # print('found it')
                new_node = child
                break
        for child_condition in node.conditional_children.keys():
            # print('conditional child', child_condition)
            if last_value == child_condition:
                # print('Found conditional')
                abbreviation = node.conditional_children[
                    last_value
                ].abbreviation
                if prefix == abbreviation:
                    # print('    mathed conditioned', )
                    new_node = node.conditional_children[last_value]
                    break
        if new_node is None:
            print('ERROR')
            break
        last_value = value
        node = new_node

    return start_level_raw, node


def print_directory_path(directory, color=colors.RED, base_level=0):
    for level, dirpart in enumerate(directory.split(os.sep)):
        print(color + '    ' * (base_level + level) + dirpart + colors.ENDC)


def walk_and_check_dirtree(directory, nodes, basedir, id_handler, level=0):
    """

    Parameters
    ----------
    directory : str
        Directory to check
    nodes :

    basedir :

    level : int, default: 0

    """
    directory_name = os.path.basename(os.path.abspath(directory))
    relpath = os.path.relpath(
        directory,
        basedir
    )

    # the nodes list contains all dir levels allowed for this level
    print('    ' * level + 'Directory', relpath)

    # print(
    #     '    ' * level + 'Corresponding tree entry',
    #     [node.name for node in nodes])

    # We allow some directories that can contain arbitrary information.
    # Don't test them
    passive_directories = [
        'Documentation',
    ]
    if directory_name in passive_directories:
        print('    ' * (level + 1) + "Passive directory, will not be analysed")
        return

    # We also ignore .* directories - these are only used for temporary data
    if directory_name.startswith('.'):
        print(
            '    ' * (level + 1) +
            "Directory starts with a dot, will not be analysed"
        )
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
        print('-' * 80)
        print(
            '    ' * level +
            'ERROR: Did not find a suitable allowed directory level '
            'for this directory:', relpath
        )
        print_directory_path(relpath, colors.RED, base_level=level)
        print(
            '    ' * level +
            'Allowed levels are:',
            ['{} ({})'.format(node.name, node.abbreviation) for node in nodes])
        print('-' * 80)
        return
    # print(node.name, node.abbreviation, node)
    # TODO: Any level-specific tests could now be called here using the node
    # variable, which could also directly store these tests.

    # for this node, call all check functions
    found_something = False
    node_output = ''
    for check_label, check_function in node.checks.items():
        # print('@@@@@@@@@@@@@@@@@@ CHECK', check_label)
        node_output += '    ' * (level + 1) + check_label + ' '
        check_value, error_msg = check_function(
            os.path.relpath(
                os.path.abspath(directory),
                start=basedir
            ),
            id_handler=id_handler,
        )
        if check_value == 0:
            node_output += colors.GREEN
        elif check_value == 1:
            found_something = True
            node_output += colors.YELLOW
        elif check_value == 2:
            found_something = True
            node_output += colors.RED

        node_output += error_msg.replace(
            '\n', '\n' + '    ' * (level + 2)
        ).rstrip()
        node_output += colors.ENDC
        node_output += '\n'
    if found_something:
        print(node_output)

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
                walk_and_check_dirtree(
                    subdir, child_nodes, basedir, id_handler, level + 1)
    else:
        # do not continue of there are no remaining node children
        if len(node.children) == 0:
            return

        for subdir in subdirs:
            walk_and_check_dirtree(
                subdir, node.children, basedir, id_handler, level + 1)


def main():
    args = handle_args()

    if args.tree is None:
        # assume pwd as directory
        directory = os.getcwd()
    else:
        directory = args.tree
        assert os.path.isdir(directory), 'Argument is not a valid directory'

    print('Working in directory', directory)
    dr_root = find_data_root(directory)
    assert dr_root is not None, 'cannot find dr data root, must begin with dr_'

    # initiate the check
    print('#' * 80)
    print(
        'Checking directory structure of directory: {}'.format(
            dr_root
        )
    )
    print('.' * 80)

    init_level = dr_root
    init_node = tree
    if args.level is not None:
        assert os.path.isdir(args.level), \
            "-l/--level must point to a valid directory within the data tree!"

        p_dr_root = Path(dr_root)
        p_level = Path(os.path.abspath(args.level))
        assert p_dr_root in p_level.parents, \
            "-l/--level must be a subdirectory of the data tree"

        start_level, start_node = _get_starting_node(args.level, tree, dr_root)
        assert start_node is not None, "ERROR"
        init_level = start_level
        init_node = start_node

    # re-scan the complete directory for ids
    id_handler = id_handling.data_id_handler(
        dr_root,
        try_cache=True,
        update_cache=False,
    )

    # TODO: I forgot what the basedir parameter actually does
    walk_and_check_dirtree(
        init_level,
        [init_node, ],
        basedir=os.getcwd(),
        id_handler=id_handler,
        # basedir=dr_root,
        level=0
    )
    print('#' * 80)


if __name__ == '__main__':
    main()
