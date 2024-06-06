#!/usr/bin/env python
"""Check a data tree for consistency

TODOS:

    * restructure to be used programatically. It would be nice to get defined
    return values so we can easily check if a directory tree is consistent.

"""
import os
import sys

from ubg_data_toolbox.dirtree import tree
from ubg_data_toolbox.dirtree_nav import find_data_root


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


def print_directory_path(directory, color=colors.RED, base_level=0):
    for level, dirpart in enumerate(directory.split(os.sep)):
        print(color + '    ' * (base_level + level) + dirpart + colors.ENDC)


def walk_and_check_dirtree(directory, nodes, basedir, level=0):
    """

    Parameters
    ----------
    directory : str
        Directory to check
    nodes :

    """
    dr_root = find_data_root(directory)
    directory_name = os.path.basename(os.path.abspath(directory))
    # print('@@@')
    # print(directory)
    # print(dr_root)
    relpath = os.path.relpath(directory, os.path.dirname(dr_root))

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
    for check_label, check_function in node.checks.items():
        # print('@@@@@@@@@@@@@@@@@@ CHECK', check_label)
        print('    ' * (level + 1) + check_label, ' ', end='')
        check_value, error_msg = check_function(
            os.path.relpath(
                os.path.abspath(directory),
                start=basedir
            )
        )
        if check_value == 0:
            print(colors.GREEN, end='')
        elif check_value == 1:
            print(colors.YELLOW, end='')
        elif check_value == 2:
            print(colors.RED, end='')

        print(error_msg.replace('\n', '\n' + '    ' * (level + 2)), end='')
        print(colors.ENDC)

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
                    subdir, child_nodes, basedir, level + 1)
    else:
        # do not continue of there are no remaining node children
        if len(node.children) == 0:
            return

        for subdir in subdirs:
            walk_and_check_dirtree(subdir, node.children, basedir, level + 1)


def main():
    if len(sys.argv) == 2:
        directory = sys.argv[1]
        assert os.path.isdir(directory), 'Argument is not a valid directory'
    else:
        # assume pwd as directory
        directory = os.getcwd()

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
    # TODO: I forgot what the basedir parameter actually does
    walk_and_check_dirtree(
        dr_root, [tree, ],
        basedir=os.getcwd(),
        # basedir=dr_root,
        level=0
    )
    print('#' * 80)


if __name__ == '__main__':
    main()
