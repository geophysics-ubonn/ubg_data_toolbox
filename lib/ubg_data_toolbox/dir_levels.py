"""
Define directory levels for the data structure (but not the structure itself)
"""
from ubg_data_toolbox.dir_level_checks import check_m_label_and_directory_match
from ubg_data_toolbox.dir_level_checks import check_m_metadata_ini_exists
from ubg_data_toolbox.dir_level_checks import check_m_empty_directories
from ubg_data_toolbox.dir_level_checks import \
    check_m_metadata_has_required_and_nonempty_entries
from ubg_data_toolbox.dir_level_checks import check_m_metadata_contents


class GlobalCounter():
    """
    A counter singleton
    """
    class_dict = {'count': -1}

    def __init__(self):
        self.__dict__ = GlobalCounter.class_dict

    def get_next_free_number(self):
        self.count += 1
        return self.count


class directory_level(object):
    def __init__(self, **kwargs):
        """
        """
        # the displayed name of the directory level
        # Note that duplicates are, in theory possible as we track unique
        # levels with the .unique_name property further below
        self.name = kwargs.get('name', None)
        # to which metadata entry does this level maps
        # This is usually a two-item tuple/list: [category, key]
        # Metadata is grouped into categories
        # (e.g., "general", "field", "laboratory")
        self.md_mapping = kwargs.get('md_mapping', None)
        self.abbreviation = kwargs.get('abbreviation', None)
        self.required = kwargs.get('required', True)
        self.description = kwargs.get('description', 'NA')

        # NOTE: We assume that if there are conditional children, then no
        # "normal" children need to be assumed
        # sometimes we branch based on the value of this directory level
        # TODO: Document the specific structure of conditions
        # TODO: Check if we can check against categories other than 'general'
        self.conditional_children = kwargs.get('conditional_children', {})

        # all other requirements go here
        children = kwargs.get('children', [])
        self.children = children

        self.counter = GlobalCounter()
        self.unique_name = 'id{:02}{}'.format(
            self.counter.get_next_free_number(),
            self.name.replace(' ', '_')
        )

        self.checks = kwargs.get('checks', {})

    def __repr__(self):
        _repr = '\n'.join((
            'Directory entry: {}'.format(self.name),
            'short form: {}'.format(self.abbreviation),
            'Is a required directory level: {}'.format(self.required),
            'metadata-mapping: {}'.format(self.md_mapping),
        ))
        return _repr

    def add_children(self, *children):
        """add one or more children to this node.

        Return a reference to self
        """
        self.children = self.children + list(children)

        return self

    def add_conditional_child(self, value, child):
        """
        Add a child that depends on the value of a given directory level
        """
        self.conditional_children[value] = child


# ########################### level definitions go here ##################### #
data_root = directory_level(
    name='data root',
    md_mapping=None,
    abbreviation='dr',
    required=True,
    description=' '.join((
        'The data root directory.'
        'This is the first directory covered by this hierarchy.',
    )),
)

theme_complex = directory_level(
    name='theme_complex',
    md_mapping=['general', 'theme_complex'],
    abbreviation='tc',
    required=True,
    description=' '.join((
        'This is a high-level grouping level that facilitates finding data',
        'for different theme complexes. Theme complexes are the highest',
        'level of research area that we differentiate. Examples:',
        'biogeophysics, cryogeophysics, hydogeophics.',
    )),
)

target = directory_level(
    name='target',
    md_mapping=['general', 'survey_type'],
    abbreviation='t',
    required=True,
    description=''.join((
        'we split laboratory and field measurements into separate'
        'subdirectories with slightly different structure.'
        'Possible values: laboratory, field',
    )),
)

# ########################### field metadata ################################ #
site = directory_level(
    name='field_site',
    md_mapping=['field', 'site'],
    abbreviation='s',
    required=True,
    description=' '.join((
        'The general measurement region. For example, this could be a',
        'mountain or city name.'
    )),
)

area = directory_level(
    name='area',
    md_mapping=['field', 'area'],
    abbreviation='a',
    required=False,
    description=' '.join((
        'A more localized area in the general measurement region. the area',
        'is located within a test-site and refers to a specific location,',
        'i.e., one plot of a field trial or the area around a specific',
        'marker within the test-site.'
    )),
)

method_field = directory_level(
    name='method_field',
    md_mapping=['general', 'method'],
    abbreviation='md',
    required=True,
    description=' '.join((
        'The method used. Examples: ERT, sEIT, SIP, SP, T.',
        'Use compound methods if multiple methods were used and measured',
        'concurrently in one data file (e.g., SP+T or SIP+T)',
    )),
)

profile = directory_level(
    name='profile',
    md_mapping=['field', 'profile'],
    abbreviation='p',
    required=False,
    description=' '.join((
        'Specific measurement location. The profile refers to the exact'
        '(within suitable uncertainties) location of the measurement. For',
        'example, on a given field plot multiple profiles can be measured',
        'in parallel lines, effectively mapping the area. When measurement',
        'setups are modified (e.g., when a monitoring setup is upgraded,',
        'e.g., by additional/new electrodes), this could justify setting up',
        'a new profile identifier for this new setup.',
    )),
)

experiment_field = directory_level(
    name='experiment_field',
    md_mapping=['general', 'experiment'],
    abbreviation='exp',
    required=False,
    description='Structure to group multiple measurements that belong to ' +
    'one experiment (e.g., time-lapse monitoring)',
)

datetime_group_field = directory_level(
    name='datetime_group_field',
    md_mapping=['general', 'dt_group'],
    abbreviation='dtg',
    required=False,
    description='Groups multiple measurements in a time or number-related '
    'group'
)

measurement_field = directory_level(
    name='label_field',
    md_mapping=['general', 'label'],
    abbreviation='m',
    required=True,
    description='This is the deepest structure we have. Usually a number ' +
    '(zero padded) is appended after the identifier m_, followed by a short ' +
    'identifier for this measurement. This could be the starting time of ' +
    'the measurement. Examples: m_01_20170105_1231, m_02_20170105_1305.',
    checks={
        'Check empty directories:': check_m_empty_directories,
        'Check for required metadata.ini file:': check_m_metadata_ini_exists,
        'Check for required metadata entries':
            check_m_metadata_has_required_and_nonempty_entries,
        'Check metadata contents': check_m_metadata_contents,
        'Check consistency of label and dir name':
            check_m_label_and_directory_match
    },
)

# ############################# # lab ####################################### #

site_lab = directory_level(
    name='laboratory_site',
    md_mapping=['laboratory', 'site'],
    abbreviation='s',
    required=False,
    description=' '.join((
        'Location of measurement. This could be a laboratory number, or ' +
        'even the number/location of one measurement bench within one ' +
        'laboratory.',
    )),
)

group_lab = directory_level(
    name='group',
    md_mapping=['laboratory', 'group'],
    abbreviation='g',
    required=False,
    description=' '.join((
        'A group can be used to group multiple experiments. This level can be',
        'helpful for larger laboratory experimental series. For example,',
        'if multiple specimens are measured, possibly with individual',
        'calibration measurements, it makes sense to not clutter the',
        'experiment (exp) level with lots of closely associated experiments.',
    )),
)

method_lab = directory_level(
    name='method_lab',
    md_mapping=['general', 'method'],
    abbreviation='md',
    required=True,
    description=' '.join((
        'The method used. Examples: ERT, sEIT, SIP, SP, T.',
        'Use compound methods if multiple methods were used and measured',
        'concurrently in one data file (e.g., SP+T or SIP+T)',
    )),
)

experiment_lab = directory_level(
    name='experiment_lab',
    md_mapping=['general', 'experiment'],
    abbreviation='exp',
    required=False,
    description='Structure to group multiple measurements that belong to ' +
    'one experiment (e.g., time-lapse monitoring)',
)

specimen = directory_level(
    name='specimen',
    md_mapping=['laboratory', 'specimen'],
    abbreviation='spe',
    required=False,
    description='Type of specimen the measurement was conducted on' +
    '(e.g., sand-stone or oilseed-plant). ' +
    'Could also refer to an internal sample number.',
)

datetime_group_lab = directory_level(
    name='datetime_group_lab',
    md_mapping=['general', 'dt_group'],
    abbreviation='dtg',
    required=False,
    description='Groups multiple measurements in a time or number-related '
    'group'
)

measurement_lab = directory_level(
    name='label_lab',
    md_mapping=['general', 'label'],
    abbreviation='m',
    required=True,
    description='This is the deepest structure we have. Usually a number ' +
    '(zero padded) is appended after the identifier m_, followed by a short ' +
    'identifier for this measurement. This could be the starting time of ' +
    'the measurement. Examples: m_01_20170105_1231, m_02_20170105_1305.',
    checks={
        'Check empty directories:': check_m_empty_directories,
        'Check for required metadata.ini file:': check_m_metadata_ini_exists,
        'Check for required metadata entries':
            check_m_metadata_has_required_and_nonempty_entries,
    },
)
