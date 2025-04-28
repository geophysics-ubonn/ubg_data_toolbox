#!/usr/bin/env python
""" Add one measurement to a directory structure, including metadata

"""
import os
import shutil
import datetime

# import data_toolbox.checks.tree as check_tree
import argparse
import IPython
from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.shortcuts import yes_no_dialog

import ubg_data_toolbox.dm_config as dm_config
from ubg_data_toolbox.dm_metadata_user_input import ask_user_for_metadata
from ubg_data_toolbox.dm_dirtree import gen_dirtree_from_metadata
from ubg_data_toolbox.metadata import write_md_nested_dict_to_file
from ubg_data_toolbox.metadata import merge_md_dicts
import ubg_data_toolbox.checks.tree as tree_check
from ubg_data_toolbox.dm_caches import md_cache_default_values

IPython


def handle_args():
    parser = argparse.ArgumentParser(
        description='Add one measurement to a given data directory structure',
    )
    parser.add_argument(
        '-t', '--tree',
        help='Path of data tree (should start with: dr_)',
        required=True,
    )
    parser.add_argument(
        '-i', '--input',
        help='Path to measurement (data/directory/directory tree)',
        required=True,
        nargs='+',
    )

    args = parser.parse_args()
    data_tree = os.path.basename(args.tree)
    if not data_tree.startswith('dr_'):
        print('')
        print('')
        print('')
        print('!' * 80)
        print('')
        print('')
        print(
            'WARNING: Your data tree directory does not start with the ' +
            'mandatory "dr_"!'
        )
        print('')
        print('')
        print('')
        print('!' * 80)
        print('')
        print('')
    return args


def copy_research_data(data_input, dir_to_m_dir, move=False, verbose=True):
    """ Copy or move the data into the data tree.

    Note that depending on the type of the parameter data_input (file or
    directory), different schemes will be employed:

    File: If not present, create measurement substructures in dirtree and
    move/copy the file into dirtree + os.sep + 'RawData/'

    Directory: Treat this directory as a (partial) data tree and try to infer
    the measurement (m_) directory. Then move all subdirectories to dirtree.
    Note that metadata.init files will NOT be moved/copied.

    Parameters
    ----------
    data_input :

    dir_to_m_dir : str
        Measurement directory.
    """
    def _transfer_file(source, target, move=move, verbose=True):
        """Wrapper that either copies or moves a file"""
        if move is True:
            shutil.move(source, target)
            if verbose:
                print('Moved {} to {}'.format(source, target))
        else:
            shutil.copy(source, target)
            if verbose:
                print('Copied {} to {}'.format(source, target))

    def _transfer_sub_directories(
            source_dir, target_dir, move=move, act_on_files=False):
        """Transfer or Copy all files and directories from one directory to
        another. Be aware of the concept of measurement directories and, if
        required, copy files/dirs into a RawData subdirectory. Also, be able to
        only copy/move subdirectories.

        Parameters
        ----------
        source_dir : str
            Source directory from which files/directories are copied or moved
        target_dir : str
            Target directory to which files/directories are copied or moved
        move : bool, optional
            If True, then move files/directories. Otherwise copy
        act_on_files : bool, optional
            If True, also copy/move all files from source_dir to target_dir.
            Otherwise only subdirectories are moved.

        """
        # get list of directories
        subdirs = sorted(
            [x for x in os.listdir(source_dir) if os.path.isdir(
                source_dir + os.sep + x
            )]
        )
        if move is True:
            raise Exception('move not implemented yet')

        if act_on_files is True:
            file_list = sorted(
                [x for x in os.listdir(source_dir) if os.path.isfile(
                    source_dir + os.sep + x)]
            )
            for filename in file_list:
                outfile = target_dir + os.sep + filename
                assert not os.path.isfile(outfile), \
                    'target file exists ' + outfile
                shutil.copy(
                    source_dir + os.sep + filename,
                    outfile,
                )

        for subdir in subdirs:
            shutil.copytree(
                source_dir + os.sep + subdir,
                target_dir + os.sep + subdir
            )

    # print(data_input)
    # import IPython
    # IPython.embed()
    if len(data_input) > 1 or os.path.isfile(data_input[0]):
        # create output directories
        os.makedirs(dir_to_m_dir + os.sep + 'RawData')
        if len(data_input) > 1:
            for filename in data_input:
                _transfer_file(
                    filename, dir_to_m_dir + os.sep + 'RawData', verbose
                )
        else:
            _transfer_file(
                data_input[0], dir_to_m_dir + os.sep + 'RawData', verbose
            )

    elif os.path.isdir(data_input[0]):
        if tree_check.is_measurement_directory(data_input[0]):
            # copy the directory
            _transfer_sub_directories(data_input[0], dir_to_m_dir, move=move)
        else:
            print(
                'Input is not a measurement directory. It will be ' +
                'treated as a data directory and all contents will be ' +
                'moved into the RawData/ subdirectory'
            )
            datadir = dir_to_m_dir + os.sep + 'RawData'
            os.makedirs(datadir, exist_ok=True)
            _transfer_sub_directories(
                data_input[0],
                datadir,
                move=move,
                act_on_files=True,
            )


def get_defaults_from_input_dirtree(data_input):
    """ Analyze the input directory/file structure and try to infer some
    default values for the metadata input

    Parameters
    ----------
    data_input :
    """
    cache_default_input = md_cache_default_values(None)

    if len(data_input) > 1 and os.path.isfile(data_input[0]):
        pass
        raise Exception('Handling of multiple files not implemented yet')
        # TODO: Analyze file(s)
    else:
        basename = os.path.basename(data_input[0])
        if basename.startswith('m_'):
            label = basename[2:]
            cache_default_input.cache['label'] = label

            # sometimes we encode the measurement time, try to parse the first
            # part of the measurement directory
            try:
                dt_start = datetime.datetime.strptime(
                    label[0:25], '%Y%m%d_%H%M_%S_%Z%z')
                cache_default_input.set(
                    'datetime_start', '{}'.format(dt_start))
            except Exception as e:
                pass
                print('There was an exception', e)

        metadata_file = basename + os.sep + 'metadata.ini'
        if os.path.isfile(metadata_file):
            # we have an existing metadata file
            # No we need to do two things:
            # 1) read in all existing values and use those as the
            #    highest-priority default value
            # 2) make a list of all metadata entries that are not in the
            # "standard" library, i.e., that are not defined in the
            # data_toolbox
            # TODO
            pass

    return cache_default_input


def get_existing_metadata(data_input, also_return_default_cache=True):
    """
    If the data input is a directory structure, look for metadata.ini files and
    import them into a metadata dictionary for use in this import.

    If requested, also fill a cache object with the values to be used as
    default entries.

    Return None if no metadata exists.
    """
    if len(data_input) > 1 or os.path.isfile(data_input[0]):
        # if input is a file then there can be no metadata files
        if also_return_default_cache:
            return None, None
        else:
            return None
    else:
        from ubg_data_toolbox.metadata import metadata_manager
        mgr = metadata_manager(data_input[0])
        md_files = mgr.find_metadata_files()
        md = mgr.import_metadata_files_to_md_dict(md_files)

        if also_return_default_cache:
            default_cache = md_cache_default_values(None)
            default_cache.import_md_dict(md)
            return md, default_cache
        return md


def main():
    # get command line arguments
    args = handle_args()
    # only one directory is allowed, but multiple files
    if len(args.input) > 1:
        for item in args.input:
            if not os.path.isfile(item):
                print('Only one directory is allowed as input for -i/--input')
                exit()

    print_formatted_text(HTML(
        '<ansiblue>' + 80 * '-' + '</ansiblue>\n' +
        'Input: {}\n'.format(args.input) +
        'Output Data Tree: {}\n'.format(args.tree) +
        '<ansiblue>' + 80 * '-' + '</ansiblue>\n'
    ))
    config, metadata = dm_config.get_configuration(
        get_default_metadata=True,
        create_if_required=True,
    )
    # IPython.embed()
    # exit()

    # store default values here for future use
    default_cache_file = config['input_default_values']

    # Try to infer as many metadata entries as possible from the input data
    # Then, provide this data to the ask_user_for_metadata function to complete
    # the input
    # 1) last input from cache
    cache_default = md_cache_default_values(default_cache_file)

    # 2)
    cache_default.import_md_dict(metadata)

    # 3) analyze input dirtree
    input_defaults = get_defaults_from_input_dirtree(args.input)
    cache_default.merge_with_cache(input_defaults)

    # 4) look for existing metadata files
    dict_existing_md, cache_existing_md = get_existing_metadata(
        args.input, also_return_default_cache=True
    )
    cache_default.merge_with_cache(cache_existing_md)
    metadata = merge_md_dicts(metadata, dict_existing_md)

    # print('')
    # print('')
    # print('')
    # print('MERGED:')
    # print(cache_default)
    # print('')
    # print('')
    # print('')
    print_formatted_text(HTML(
        '<ansiyellow>' + 80 * '-' + '</ansiyellow>\n' +
        ' ' * 10 + 'Please enter required metadata entries:\n' +
        '<ansiyellow>' + 80 * '-' + '</ansiyellow>\n'
    ))

    # this is where we actually ask for input
    md_entries = ask_user_for_metadata(
        md_entries=metadata,
        ask_for='required',
        cache_default_values=cache_default,
    )

    print_formatted_text(HTML(
        '<ansiyellow>' + 80 * '-' + '</ansiyellow>\n' +
        ' ' * 10 + 'Optional metadata entries that have relevance for the\n' +
        ' ' * 10 + 'directory structure: \n' +
        ' ' * 10 + 'leave empty to skip this level \n' +
        '<ansiyellow>' + 80 * '-' + '</ansiyellow>\n'
    ))
    md_entries = ask_user_for_metadata(
        md_entries=metadata,
        ask_for='dirtree_optional',
        cache_default_values=cache_default,
    )

    result = yes_no_dialog(
        title='Show optional metadata parameters?',
        text='Show optional metadata parameters?'
    ).run()
    if result:
        print_formatted_text(HTML(
            '<ansiyellow>' + 80 * '-' + '</ansiyellow>\n' +
            ' ' * 10 + 'Optional metadata entries\n' +
            '<ansiyellow>' + 80 * '-' + '</ansiyellow>\n'
        ))

        md_entries = ask_user_for_metadata(
            md_entries=metadata,
            ask_for='optional',
            show_menu=True,
            cache_default_values=cache_default,
        )

    print('')
    print('')
    print('@' * 80)
    print('@' * 80)
    print('Final metadata:')
    for section in md_entries.keys():
        print('Section: ', section)
        for name, item in sorted(md_entries[section].items()):
            print(' ' * 4 + '{}: {}'.format(name, item.value))
    print('@' * 80)

    # now, create the directory tree
    dirtree = gen_dirtree_from_metadata(
        md_entries, name_of_rd=args.tree, absolute_path=True)
    print('The following directory tree will be created created:')
    print(dirtree)

    # check if this output directory already exists, abort if it does
    if os.path.isdir(dirtree):
        raise IOError('output directory already exists')

    os.makedirs(dirtree)

    # write metadata file
    write_md_nested_dict_to_file(
        md_entries,
        dirtree + os.sep + 'metadata.ini'
    )
    print(
        'Metadata file written to:',
        dirtree + os.sep + 'metadata.ini'
    )

    # copy the data
    copy_research_data(args.input, dirtree, verbose=True)

    # IPython.embed()
    # make sure that we are in a data directory structure
    # check_tree.is_in_datatree()


if __name__ == '__main__':
    main()
    # os.makedirs('test_copy', exist_ok=True)
    # indir = 'test_data/'
    # indir += 'm_20200313_0944_42_UTC+0000_std21_f10_rhizo_copper_pos02'
    # copy_research_data(indir, 'test_copy/', move=False)
