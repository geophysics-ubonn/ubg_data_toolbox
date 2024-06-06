"""
Generate a dot-language graph of the directory tree
"""


def _gen_nodes(node, blacklist=None):
    """Generate dot-node definitions"""
    if blacklist is None:
        blacklist = []
    if node.unique_name in blacklist:
        return

    if node.required:
        color = 'red'
    else:
        color = 'black'
    dot_def = '{}[label="({}) {}", color="{}"];'.format(
        node.unique_name,
        node.abbreviation,
        node.name,
        color
    )
    blacklist.append(node.unique_name)
    yield(dot_def)
    for child in node.children:
        yield from _gen_nodes(child, blacklist)
    for condition, child in node.conditional_children.items():
        yield from _gen_nodes(child, blacklist)


def _gen_connections(node, blacklist=None):
    if blacklist is None:
        blacklist = []
    if node.unique_name in blacklist:
        return

    for connect_to in node.children:
        connection = '{} -> {};'.format(
            node.unique_name,
            connect_to.unique_name
        )
        yield(connection)

    for condition, connect_to in node.conditional_children.items():
        connection = '{} -> {}[label="{}"];'.format(
            node.unique_name,
            connect_to.unique_name,
            condition,
        )
        yield(connection)

    blacklist.append(node.unique_name)
    for child in node.children:
        yield from _gen_connections(child, blacklist)

    for condition, child in node.conditional_children.items():
        yield from _gen_connections(child, blacklist)


def write_graph_to_file(filename, node):
    with open(filename, 'w') as fid:
        fid.write('# compile with:\n')
        fid.write('# dot -Tps -o dirstruc.ps ${infile}\n')
        fid.write('# ps2pdf dirstruc.ps\n')
        fid.write('# pdfcrop dirstruc.pdf\n')
        fid.write('digraph directory_structure {\n')
        for line in list(_gen_nodes(node)):
            fid.write(' ' * 4 + line + '\n')

        fid.write('\n')

        for line in list(_gen_connections(node)):
            fid.write(' ' * 4 + line + '\n')

        fid.write('}')
