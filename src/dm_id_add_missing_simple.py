#!/usr/bin/env python
import os
import pathlib
import argparse

from ubg_data_toolbox.metadata import metadata_chain
from ubg_data_toolbox import id_handling
from ubg_data_toolbox.dirtree_nav import find_data_root


class id_generator_simple(object):
    """A simple ID generator that generates alpha-numeric ID in the form
        '[PREFIX]_[SITE]_[YEAR:%04i]_[RUNNING_NR:%08i]',
    """
    def __init__(self, handler, prefix=None, start_nr=None):
        self.handler = handler
        if prefix is None or prefix == '':
            self.prefix = ''
        else:
            self.prefix = prefix + '_'
        self.next_nr = start_nr

    def gen_id(self, metadata):
        if metadata['general']['survey_type'] == 'field':
            site = metadata['field']['site'].lower()
        else:
            site = ''

        new_id = '{}{}_{}_{:04}_{:08}'.format(
            self.prefix,
            site,
            metadata['general']['method'].lower(),
            metadata['general']['datetime_start'][0:4],
            self.next_nr
        )
        self.next_nr += 1
        return new_id

    def get_next_free_id(self, metadata):
        new_id = self.gen_id(metadata)
        while self.handler.check_id_present(new_id):
            new_id = self.gen_id()
        return new_id


def handle_args():
    parser = argparse.ArgumentParser(
        description='Fill in missing ids using the Schema: ' +
        '[SITE]_[YEAR]_[RUNNING_NR]',
    )
    parser.add_argument(
        '--level',
        help='Start level (directory). Only m_ directories below this ' +
        'directory will be modified',
        required=False,
    )
    parser.add_argument(
        '--prefix',
        help='Prefix for new ids',
        required=False,
    )
    parser.add_argument(
        '--dry-run',
        help='Dry run - Do not write anything to disk',
        required=False,
        action='store_true',
    )
    args = parser.parse_args()
    return args


def main():
    args = handle_args()

    # we assume that we are located in a data tree
    # note: this could also be modified via args in the future ...
    datatree = '.'
    assert os.path.isdir(datatree), "datatree is not a directory"
    dr_root = find_data_root(datatree)
    assert dr_root is not None, 'Could not find a data root directory'

    handler = id_handling.data_id_handler(
        dr_root,
        try_cache=True,
        update_cache=False
    )

    id_gen = id_generator_simple(
        handler,
        prefix=args.prefix,
        start_nr=1,
    )

    print('Adding IDs to measurements missing an ID:')

    if args.level is not None:
        start_dir = os.path.abspath(args.level)
        assert os.path.isdir(start_dir), 'Directory {} does not exist'.format(
            start_dir
        )
        p_start = pathlib.Path(start_dir)
        p_dr = pathlib.Path(dr_root)
        if p_start != p_dr and p_dr not in p_start.parents:
            raise Exception('The subdir must be located in the data root')
    else:
        start_dir = dr_root

    print('Starting directory:', start_dir)
    m_dirs = []
    for root, dirs, files in os.walk(start_dir):
        if os.path.basename(root).startswith('m_'):
            metadata_file = root + os.sep + 'metadata.ini'
            if os.path.isfile(metadata_file):
                # print(root)
                m_dirs.append(root)

    for mdir in m_dirs:
        chain = metadata_chain(mdir)
        filename = chain.get_available_metadata_files()[0]
        config = chain._import_metadata_files((filename, ))
        need_new_id = False
        if 'id' in config['general']:
            # check that this is a valid id
            pass
        else:
            need_new_id = True
        if need_new_id:
            required_entries = [
                ('general', 'survey_type'),
                ('general', 'method'),
                ('general', 'datetime_start'),
            ]

            for section, entry in required_entries:
                if entry not in config[section]:
                    print('Cannot generate an ID due to missing metadata')
                    print('    missing entry:', entry)
                    continue

            if config['general']['survey_type'] == 'field':
                if 'site' not in config['field']:
                    print('site missing from [field] section')
                    continue

            new_id = id_gen.get_next_free_id(config)

            if args.level is not None:
                mdir_short = os.path.relpath(mdir, args.level)
            else:
                mdir_short = os.path.relpath(mdir, dr_root)
            print(
                'Assigning new id "{}" for "{}"'.format(new_id, mdir_short)
            )
            config['general']['id'] = new_id

            if not args.dry_run:
                pass
                with open(filename, 'w') as fid:
                    config.write(fid)

    if args.dry_run:
        print('')
        print('')
        print('-' * 80)
        print("WARNING WARNING WARNING")
        print('This was a dry-run, no changes were written to disk!')


if __name__ == '__main__':
    main()
