import os


def is_in_datatree(directory=None):
    """

    """
    cwd = os.getcwd()
    items = cwd.spli(os.sep)

    raise Exception('Implementation not complete!')


def is_measurement_directory(directory):
    """Check if the provided directory is a measurement directory

    Parameters
    ----------
    directory : str

    """
    is_meas_dir = True

    if not os.path.isdir(directory):
        print('Is not a directory', directory)
        is_meas_dir = False

    if not os.path.basename(directory).startswith('m_'):
        print('Does not start with identifier: "m_"')
        is_meas_dir = False

    rawdata_dir = directory + os.sep + 'RawData'
    if not os.path.isdir(rawdata_dir):
        print('RawData directory not present', rawdata_dir)
        is_meas_dir = False

    metadata_file = directory + os.sep + 'metadata.ini'
    if not os.path.isfile(metadata_file):
        print('metadata.ini file not present', metadata_file)
        is_meas_dir = False

    return is_meas_dir
