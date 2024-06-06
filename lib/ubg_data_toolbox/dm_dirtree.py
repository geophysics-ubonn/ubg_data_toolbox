import os

from ubg_data_toolbox.dirtree import tree


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
