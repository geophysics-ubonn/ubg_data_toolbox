"""Level-specific checks

See ubg_data_toolbox.dir_levels for usage

Naming convention: check_[level abbreviation]_[short_description]
"""
import os
import datetime

CHECK_OK = 0
CHECK_WARNING = 1
CHECK_NOT_OK = 2

bool_converter = {
    True: CHECK_OK,
    False: CHECK_NOT_OK,
}


def check_m_metadata_ini_exists(directory):
    """Check if the metadata.ini file exists in the given directory
    """
    check_result = os.path.isfile(directory + os.sep + 'metadata.ini')
    error_msg = 'ok'
    if not check_result:
        error_msg = 'Did not find required metadata.ini file in {}'.format(
            directory
        )
    return bool_converter[check_result], error_msg


def _check_metadata_datetime_is_correct_format(md):
    """We require that datetimes are provided in UTC, in one of multiple
    formats

    """
    error_msg = '\n'
    # check these entries for proper datetimes
    # tuples include (section, key) pairs
    entries_to_check = [
        ('general', 'datetime_start'),
        ('general', 'datetime_end'),
    ]

    allowed_formats = (
        '%Y%m%d',
        '%Y%m%d_%H%M',
        '%Y%m%d_%H%M_%S',
    )
    # import IPython
    # IPython.embed()
    all_good = True
    for (section, entry) in entries_to_check:
        value = md[section][entry].value
        if value is not None and value != '':
            valid_conversion = False
            for dt_format in allowed_formats:
                try:
                    datetime.datetime.strptime(
                        md[section][entry].value,
                        dt_format
                    )
                    valid_conversion = True
                except ValueError:
                    # print(e)
                    # ignore the conversion error
                    pass
            all_good = all_good & valid_conversion
            if valid_conversion:
                msg = 'OK: [{}][{}]\n'.format(section, entry)
            else:
                msg = 'FAIL: [{}][{}] is not a valid date format!'.format(
                        section, entry
                    )
            error_msg += msg
    return all_good, error_msg


def check_m_metadata_contents(directory):
    """Overall check for all metadata contents (i.e., correct date formats,
    etc)
    """
    # read in available metadata
    from ubg_data_toolbox.metadata import metadata_chain
    chain = metadata_chain(directory)
    md = chain.get_merged_metadata()

    # now call the subchecks
    check_result, error_msg = _check_metadata_datetime_is_correct_format(md)

    # for now just return this. When we get more checks, return values need to
    # be aggregated
    if not check_result:
        return_value = CHECK_NOT_OK
    else:
        return_value = CHECK_OK
    return return_value, error_msg


def check_m_metadata_has_required_and_nonempty_entries(directory):
    # be careful with importing at the beginning of the file: circular imports
    # possible!
    from ubg_data_toolbox.metadata import metadata_chain
    chain = metadata_chain(directory)
    md = chain.get_merged_metadata()

    if md['general']['survey_type'].value is None:
        error_msg = '\n[general] survey_type must be present in order to '
        error_msg += 'fully assess the presence of required fields!'
        return CHECK_NOT_OK, error_msg

    # we have a survey type
    survey_type = md['general']['survey_type'].value
    assert survey_type in ['field', 'laboratory'], \
        "metadata.ini: [general] survey_type must be 'field' or 'laboratory'"

    # later we need to check if a given entry is required for this survey_type
    check_key = 'required_{}'.format(
        {
            'field': 'field',
            'laboratory': 'lab',
        }[survey_type]
    )

    # import IPython
    # IPython.embed()
    # exit()

    error_msg = ''
    check_result = CHECK_OK
    for section in md.keys():
        for key, item in md[section].items():
            # is this item required
            if getattr(item, check_key):
                # if .value is None, this means we do not have this entry in
                # the metadata.ini file
                if item.value is None:
                    error_msg += ''.join((
                        'Required entry [{}]-{} is missing\n'.format(
                            section,
                            key
                        )
                    ))
                    check_result = CHECK_NOT_OK
                # check if it is empty
                elif item.value == '':
                    error_msg += ''.join((
                        'Required entry [{}]-{} is empty\n'.format(
                            section,
                            key
                        )
                    ))
                    check_result = CHECK_NOT_OK
    if check_result == CHECK_OK:
        error_msg = 'ok'
    else:
        error_msg = '\n' + error_msg
    return check_result, error_msg


def check_m_empty_directories(directory):
    """We would like to recommend to not create certain directories empty
    """
    dirs_that_shouldnt_be_empty = (
        'Pictures',
        'Misc',
        'DataProcessed',
        'Analysis',
    )
    error_msg = ''
    check_result = CHECK_OK
    for subdir in dirs_that_shouldnt_be_empty:
        fullpath = directory + os.sep + subdir
        if os.path.isdir(fullpath) and len(os.listdir(fullpath)) == 0:
            error_msg += '{} is empty\n'.format(subdir)
            check_result = CHECK_WARNING

    if error_msg == '':
        error_msg = 'ok'

    return check_result, error_msg
