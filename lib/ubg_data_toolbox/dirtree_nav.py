# navigate within a dirtree
import os


def find_data_root(directory):
    """Given a relative or absolute directory path, try to find a directory
    that corresponds to the data root of the data management tree

    Parameters
    ----------
    directory : str
        Directory to start with

    Returns
    -------
    data_root : None|str
        None if we did not find a data root directory. Otherwise, return the
        full absolute path to the data root
    """
    assert os.name != 'nt', 'This function does not work under windows, fix it'
    testdir = os.path.normpath(os.path.abspath(directory))
    dr_data_root = None
    # WARNING: TODO: Will not work under Windows
    while testdir != '/':
        base, part = os.path.split(testdir)
        if part.startswith('dr_'):
            dr_data_root = testdir
        testdir = base
    return dr_data_root


def get_dirtree_values(directory):
    """If directory is located within a proper data directory structure, then
    return a dict containing the abbreviations as keys, and the assigned values
    as values.

    Parameters
    ----------
    directory : str
        Directory to start with

    Returns
    -------
    presets : dict
        keys are the abbreviations, values the values inferred from the
        directory names

    """
    data_root = find_data_root(os.path.abspath(directory))
    presets = {}
    if data_root is not None:
        # only try to fill in defaults if we have a valid directory structure
        basedir = os.path.dirname(data_root)
        # get our directory structure within the data directory
        treeitems = os.path.relpath(os.getcwd(), basedir).split('/')
        for item in treeitems:
            index = item.find('_')
            if index > 0:
                abbreviation = item[0:index]
                value = item[index + 1:]
                presets[abbreviation] = value
    return presets
