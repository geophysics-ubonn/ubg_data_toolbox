"""
Define the directory structure using a tree structure

Note that the first child is the one used while when auto-generating
directories.

Also, direct children should be placed first to facilitate generation of latex
tables for the directory levels.
"""
from ubg_data_toolbox import dir_levels as dl

tree = dl.data_root.add_children(dl.theme_complex)

dl.theme_complex.add_children(dl.target)

# field branch
dl.target.add_conditional_child('field', dl.site)

dl.site.add_children(dl.area, dl.method_field)

dl.area.add_children(dl.method_field)

dl.method_field.add_children(
    dl.profile, dl.measurement_field, dl.datetime_group_field, dl.experiment_field
)

dl.profile.add_children(
    dl.experiment_field, dl.datetime_group_field, dl.measurement_field
)

dl.experiment_field.add_children(
    dl.datetime_group_field, dl.measurement_field
)

dl.datetime_group_field.add_children(dl.measurement_field)

# lab branch
dl.target.add_conditional_child('laboratory', dl.site_lab)

dl.site_lab.add_children(dl.group_lab, dl.method_lab)
dl.group_lab.add_children(dl.experiment_lab)
dl.experiment_lab.add_children(dl.method_lab)
dl.method_lab.add_children(
    dl.specimen, dl.measurement_lab, dl.datetime_group_lab
)
dl.specimen.add_children(dl.measurement_lab, dl.datetime_group_lab)
dl.datetime_group_lab.add_children(dl.measurement_lab)
