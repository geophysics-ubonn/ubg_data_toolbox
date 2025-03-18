"""

"""
import os

from ubg_data_toolbox.dirtree_nav import find_data_root
from ubg_data_toolbox.dirtree_nav import get_dirtree_values
from ubg_data_toolbox.dirtree import tree
from ubg_data_toolbox.metadata_definitions import metadata_tree
from ubg_data_toolbox.metadata_definitions import get_empty_metadata_tree
import ubg_data_toolbox.dir_levels


def _dirtree_next_level(node, md_entries, override_name=None):
    """

    """
    # print('@ processing node', node.name)
    do_not_proceed = False
    # if no metadata mapping exists, assume we always want this level
    # this is probably not correct...
    if override_name is not None:
        yield override_name
    else:
        # find the meta data entry
        section, key = node.md_mapping
        metadata = md_entries[section][key]
        value = metadata.value
        # check if we have a valid label for this node
        if value is not None and value != '':
            yield node.abbreviation + '_' + value
        else:
            # print('@ No VALUE')
            # meta data not set, abort here
            if metadata.required_lab or metadata.required_field:
                do_not_proceed = True
            else:
                pass

    # now go to the next level
    # print('@ do not proceed', do_not_proceed)
    if not do_not_proceed:
        if len(node.conditional_children) > 0:
            # print(
            #     '@ next conditional child',
            #     node.conditional_children[value])
            if value in node.conditional_children:
                # we can assume that value was already set
                yield from _dirtree_next_level(
                    node.conditional_children[value],
                    md_entries
                )
            else:
                # value wrong
                pass
        else:
            # print('@ proceeding to next normal child, from', node.name)
            # use first "normal" child
            if len(node.children) > 0:
                yield from _dirtree_next_level(node.children[0], md_entries)


def gen_dirtree_from_metadata(
        md_entries, name_of_rd='dr_data root', absolute_path=False):
    """Given a set of (partially filled) metadata entries, generate the
    directory tree as far as possible

    Parameters
    ----------
    md_entries :

    name_of_rd : str, optional

    absolute_path : bool, optional
    """
    dirtree_list = list(
        _dirtree_next_level(tree, md_entries, override_name=name_of_rd)
    )

    dirtree = os.path.join(*dirtree_list)
    if absolute_path:
        dirtree = os.path.abspath(dirtree)

    return dirtree


def check_mdir_is_proper(mdir):
    """Check that a given directory path points to a valid measurement
    directory

    Parameters
    ----------
    mdir : str
        Path to m_dir

    """
    mdir_full = os.path.abspath(mdir)
    is_valid = True
    if find_data_root(mdir_full) is None:
        is_valid = False
    if not os.path.isdir(mdir_full):
        is_valid = False
    if not os.path.basename(mdir_full).startswith('m_'):
        is_valid = False

    return is_valid


def gen_metadata_from_mdir(mdir, metadata=None):
    """Generate metadata, given the path of a measurement directory

    Parameters
    ----------
    mdir : str
        Path to an measurement directory. Can be a relative value
    metadata : None|ubg_data_toolbox.metadata_definitions.metadata_tree

    """
    mdir_full = os.path.abspath(mdir)
    assert check_mdir_is_proper(mdir_full)

    if metadata is None:
        # get an empty metadata tree
        metadata = get_empty_metadata_tree()

    presets = get_dirtree_values('.')

    def update_md(
            metadata: metadata_tree,
            node: ubg_data_toolbox.dir_levels.directory_level,
            presets: dict):

        if node.abbreviation not in presets:
            return
        value = presets[node.abbreviation]
        presets.pop(node.abbreviation)

        if node.md_mapping is not None:
            category, key = node.md_mapping
            metadata[category][key].value = value

        if len(node.conditional_children) > 0:
            if value not in node.conditional_children:
                return
            update_md(metadata, node.conditional_children[value], presets)
        else:
            for child in node.children:
                update_md(metadata, child, presets)

    update_md(metadata, tree, presets)
    return metadata
