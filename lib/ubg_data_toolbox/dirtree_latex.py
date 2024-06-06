import ubg_data_toolbox.dirtree as dirtree


def gen_description_table_latex():
    output_lines = []
    ids_already_processed = []

    bool_converter = {
        True: 'y',
        False: 'n',
    }

    def walk_tree(node):
        # print(node.unique_name)
        if node.unique_name not in ids_already_processed:
            output_lines.append(
                r'{} & {} & {} & {} \\'.format(
                    node.name.replace('_', r'\_'),
                    node.abbreviation,
                    bool_converter[node.required],
                    node.description.replace('_', r'\_')
                )
            )
            ids_already_processed.append(node.unique_name)

        for child in node.children:
            walk_tree(child)
        for condition, child in node.conditional_children.items():
            output_lines.append(r'\hline')
            output_lines.append(
                r'{}'.format(
                    node.name.replace('_', r'\_')
                ) + r' = \textbf{' + '{}'.format(condition) + r'}:\\'
            )
            walk_tree(child)
            output_lines.append(r'\hline')

    output_lines.append(r'\begin{longtable}{c|c|c|p{10cm}}')
    output_lines.append(r'key & abbreviation & required & description\\')
    output_lines.append(r'\hline')
    walk_tree(dirtree.tree)
    output_lines.append(r'\end{longtable}')
    return "\n".join(output_lines)


def write_table_to_file(filename):
    table = gen_description_table_latex()
    with open(filename, 'w') as fid:
        fid.write(table)
