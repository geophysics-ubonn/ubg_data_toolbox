#!/usr/bin/env python
import os
import argparse

from ubg_data_toolbox.metadata import metadata_chain
from ubg_data_toolbox import id_handling
from ubg_data_toolbox.dirtree_nav import find_data_root


def handle_args():
    parser = argparse.ArgumentParser(
        description='Fill in missing ids using the Schema: ' +
        '[SITE]_[YEAR]_[RUNNING_NR]',
    )
    # parser.add_argument(
    #     '-p',
    #     help='Prefix for new ids',
    #     required=True,
    # )
    args = parser.parse_args()
    return args


def main():
    args = handle_args()
    args

    # we assume that we are located in a data tree
    # note: this could also be modified via args in the future ...
    datatree = '.'
    assert os.path.isdir(datatree), "datatree is not a directory"
    dr_root = find_data_root(datatree)
    assert dr_root is not None, 'Could not find a data root directory'

    handler = id_handling.data_id_handler(dr_root, try_cache=False)

    print('Adding IDs to measurements without one:')

    m_dirs = []
    for root, dirs, files in os.walk(dr_root):
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

            prefix = '{}_{}_{}_'.format(
                config['field']['site'].lower(),
                config['general']['method'].lower(),
                config['general']['datetime_start'][0:4],
            )

            class id_generator(object):
                def __init__(self, prefix, start_nr, handler):
                    self.prefix = prefix.replace(' ', '_')
                    self.nr = start_nr
                    self.handler = handler

                def gen_id(self):
                    new_id = '{}_{:08}'.format(
                        self.prefix,
                        self.nr
                    )
                    self.nr += 1
                    return new_id

                def get_next_free_id(self):
                    new_id = self.gen_id()
                    while self.handler.check_id_present(new_id):
                        new_id = self.gen_id()
                    return new_id

            generator = id_generator(prefix, 0, handler)
            new_id = generator.get_next_free_id()

            print('Assigning new id {} for {}:', new_id, mdir)
            config['general']['id'] = new_id

            with open(filename, 'w') as fid:
                pass
                config.write(fid)


if __name__ == '__main__':
    main()
