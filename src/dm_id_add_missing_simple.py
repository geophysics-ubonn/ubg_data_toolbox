#!/usr/bin/env python
import os
import argparse

from ubg_data_toolbox.metadata import metadata_chain


def handle_args():
    parser = argparse.ArgumentParser(
        description='Fill in missing ids using the Schema: ' +
        '[SITE]_[YEAR]_[RUNNING_NR',
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

    print('Adding IDs to measurements without one:')
    runnings_ids = {

    }

    running_id_nr = 0

    m_dirs = []
    for root, dirs, files in os.walk('.'):
        if os.path.basename(root).startswith('m_'):
            metadata_file = root + os.sep + 'metadata.ini'
            if os.path.isfile(metadata_file):
                # print(root)
                m_dirs.append(root)

    for mdir in m_dirs:
        print(mdir)
        chain = metadata_chain(mdir)
        filename = chain.get_available_metadata_files()[0]
        config = chain._import_metadata_files((filename, ))
        print(config['general'])
        need_new_id = False
        if 'id' in config['general']:
            # check that this is a valid id
            pass
        else:
            need_new_id = True
        if need_new_id:
            print('Constructing new id')
            required_entries = [
                ('general', 'survey_type'),
                ('general', 'method'),
                ('general', 'datetime_start'),
            ]

            for section, entry in required_entries:
                if entry not in config[section]:
                    print('Cannot generate an ID due to missing metadata')
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
            print('prefix:', prefix)
            print('Assigning new id', mdir)
            new_id = 'ubg_{:08}'.format(running_id_nr + 1)
            print('New id:', new_id)
            config['general']['id'] = new_id
            # save
            # with open(filename, 'w') as fid:
            #     pass
            #     config.write(fid)
            running_id_nr += 1


if __name__ == '__main__':
    main()
