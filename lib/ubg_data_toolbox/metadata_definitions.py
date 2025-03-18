"""
Define meta data entries and, where possible, map them to the directory levels

"""
import os
import configparser

import ubg_data_toolbox.dir_levels as dir_levels


class colors:
    """
    Usage:

        print(colors.RES + 'STRING' + colors.ENDC)

    """
    RED = '\033[31m'
    ENDC = '\033[m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'


class metadata_tree(dict):
    def __init__(self, input_dict):
        self.update(input_dict)

    def __repr__(self):
        representation = ''

        # try to determine if we are dealing with a field or a laboratory
        # measurement
        if self['general']['survey_type'].value is None:
            warning_color = colors.YELLOW
            representation += ''.join((
                '!!! WARNING: general - survey_type not set - ',
                'cannot determine required fields\n'
            ))
        else:
            warning_color = colors.RED

        # we know this is a nested dict
        for section in self.keys():
            subrepr = ''

            for key, item in self[section].items():
                if item.value is not None:
                    subrepr += '    {}: {}\n'.format(key, item.value)
                else:
                    # check it this entry is required
                    if item.required_field or item.required_lab:
                        subrepr += warning_color
                        subrepr += '    {}'.format(key)
                        subrepr += colors.ENDC + '\n'

            if subrepr != '':
                representation += 'Section: {}\n'.format(section)
                representation += subrepr
        return representation

    def to_file(self, filename, overwrite=False):
        """Write metadata to file (usually a metadata.ini file)

        Parameters
        ----------
        filename: str
            Path of new filename

        """
        if os.path.isfile(filename):
            print('metadta.ini already exists')
            if not overwrite:
                print('will not overwrite')
                return
        cfg_file = configparser.ConfigParser(comment_prefixes=None)

        for section in self.keys():
            cfg_file.add_section(section)
            for key in self[section].keys():
                value = self[section][key].value
                if value is not None:
                    cfg_file[section][key] = value
        with open(filename, 'w') as fid:
            cfg_file.write(fid)


class md_entry(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', None)
        # self.section = kwargs.get('section', None)
        self.required_field = kwargs.get('required_field', False)
        self.required_lab = kwargs.get('required_lab', False)
        # some entries are not required for the metadata itself, but can
        # optionally be of used as levels in the directory structure.
        # We want to be able to just ask for these dirtree-optional items
        # instead of asking for all optional items
        self.dirtree_optional = kwargs.get('dirtree_optional', False)
        self.multiline = kwargs.get('multiline', False)
        self.dublin_core = kwargs.get('dublin_core', None)
        self.description = kwargs.get('description', None)
        # regarding the loose mapping of metadata to the directory structure,
        # we here define the level on which we would prefer the entry to be
        # located. Note that the entry must not be defined above this level due
        # to logical constraints! For example, it does not make sense to define
        # a measurement type for a site.
        # plevel is either a list or None
        #     the list contains either one or two entries
        #     one entry means that this plevel is used in both field and lab
        #     two entries correspond to [field, lab] entries
        self.plevel = kwargs.get('plevel', None)
        self.data_type = str
        # sometime we want to restrict possible values
        self.allowed_values = kwargs.get('allowed_values', None)
        # this should be a dict or None
        # if this is a dict, we expect the keys to be instances of md_entry,
        # and the value to be either a value, or a tuple of values
        # A tuple () indicates that the md_entry.value should be one of the
        # tuple entries
        self.conditions = kwargs.get('conditions', None)
        # in case some potential values come up regularly, we can store them
        # in here to facilitate auto completion.
        self.autocomplete = kwargs.get('autocomplete', None)
        # this variable is used to store actual values when we construct
        # meta data
        self.value = kwargs.get('value', None)
        # This setting can be used to indicate a newly, on-the-fly created
        # metadata set. This can happen if existing metadata files are imported

        # with new keys/sections
        self.is_extra = kwargs.get('is_extra', False)

    def is_empty(self):
        # Return True if the value is None or ''
        if self.value is None or self.value == '':
            return True
        return False

    def conditions_are_met(self):
        """Checks if all conditions were met
        """
        if self.conditions is None:
            return True

        print('Checking conditions')
        all_met = True
        for entity, value in self.conditions.items():
            if isinstance(value, tuple):
                print('Checking tuple')
                check = (entity.value in value)
            else:
                print('Checking singular value')
                check = (entity.value == value)
                print('    check result:', check)
            if not check:
                all_met = False
        print('')
        return all_met


def get_md_values():
    """ Get an instance of the metadata entry structure
    """

    md_survey_type = md_entry(
        name='survey_type',
        # section='general',
        required_field=True,
        required_lab=True,
        multiline=False,
        dublin_core=None,
        description='Field or laboratory measurements? ' +
        'Allowed values: field, laboratory',
        plevel=dir_levels.target,
        data_type=str,
        allowed_values=['field', 'laboratory'],
    )

    md_method = md_entry(
        name='method',
        required_field=True,
        required_lab=True,
        multiline=False,
        dublin_core=False,
        description='Which method(s) were used? (e.g.: ERT, SP, GPS, GPR)',
        plevel=[dir_levels.method_field, dir_levels.method_lab],
        data_type=str,
        allowed_values=None,
        autocomplete=[
            'sEIT',
            'ERT',
            'TDIP',
            'SP',
            'GPR',
            'TEMP',
            'MAG',
            'GPS'
        ],
    )

    md_site = md_entry(
        name='site',
        required_field=True,
        required_lab=False,
        multiline=False,
        dublin_core=None,
        description='The general area of the measurement, e.g. a town name. ' +
        'This is further ' +
        'clarified in the metadata entries "area", "profile", "coordinates"',
        plevel=dir_levels.site,
        data_type=str,
        allowed_values=None,
        conditions={
            md_survey_type: 'field',
        }
    )

    md_area = md_entry(
        name='area',
        required_field=True,
        required_lab=False,
        multiline=False,
        dublin_core=None,
        description='A more localized specification of the measurement ' +
        'area, e.g., an identifier of a certain field or street',
        plevel=dir_levels.area,
        data_type=str,
        allowed_values=None,
        conditions={
            md_survey_type: 'field',
        },
    )

    md_profile = md_entry(
        name='profile',
        required_field=True,
        required_lab=False,
        multiline=False,
        dublin_core=None,
        description=''.join((
            'The profile that was measured on. One common naming scheme ',
            'consistent of the character "p",a running number, and ',
            'a signifying key word. Example: p_01_nor.',
            'Use "complete_area" for unspecific locations, i.e., whole-day ',
            'gps measurements at one location'
        )),
        plevel=dir_levels.profile,
        data_type=str,
        allowed_values=None,
        conditions={
            md_survey_type: 'field',
        },
    )

    md_experiment = md_entry(
        name='experiment',
        required_field=False,
        required_lab=False,
        dirtree_optional=True,
        multiline=False,
        dublin_core=None,
        description=''.join((
            'Label for the experiment that a measurement is assigned to',
        )),
        plevel=[dir_levels.experiment_field, dir_levels.experiment_lab],
        data_type=str,
        allowed_values=None,
    )

    md_datetime_start = md_entry(
        name='datetime_start',
        required_field=True,
        required_lab=True,
        multiline=False,
        dublin_core='date',
        description=''.join((
            'Starting datetime of the measurement/measurements. ',
            'Use date format YYYYmmdd_HHMM_s . ',
            'YYYY: Year (e.g., 2004), mm: Month, dd: Day of month, ',
            'HH: hour (1-24), MM: Minute (1-60), SS: Second ',
            'Leave unknown parts out (e.g., seconds)',
        )),
        plevel=[
            dir_levels.datetime_group_field, dir_levels.datetime_group_lab],
        data_type=str,
        allowed_values=None,
    )

    md_label = md_entry(
        name='label',
        required_field=True,
        required_lab=True,
        multiline=False,
        dublin_core=None,
        description=''.join((
            'Label of the individual measurement, This is the identifier for ',
            'a given measurement at a given profile. Usually we construct ',
            'the label using three parts: ',
            'datetime, running number, one or two important keywords. ',
            'Example: 20240516_01_p1_nor',
        )),
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
    )

    md_description = md_entry(
        name='description',
        required_field=True,
        required_lab=True,
        multiline=True,
        dublin_core='description',
        description=''.join((
            'Description (should be short, comprehensive, and with links to '
            'detailed documentation)'
        )),
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
    )

    md_restrictions = md_entry(
        name='restrictions',
        required_field=False,
        required_lab=False,
        multiline=True,
        dublin_core='license',
        description='State any licensing restriction of the data set. ' +
        'Especially, note down any copyright owned by a party that is not ' +
        'the Department of Geophysics, Uni Bonn',
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
    )
    md_completed = md_entry(
        name='completed',
        required_field=True,
        required_lab=True,
        multiline=False,
        dublin_core=None,
        description=''.join((
            'States if the measurement series is finished or still ongoing. ',
            'Possible values: yes, no',
        )),
        plevel=[
            dir_levels.datetime_group_field, dir_levels.datetime_group_lab],
        data_type=str,
        allowed_values=['yes', 'no'],
    )

    md_person_responsible = md_entry(
        name='person_responsible',
        required_field=True,
        required_lab=True,
        multiline=False,
        dublin_core='creator',
        description=''.join((
            'The person that is responsible for this data set. '
            'This must not necessarily be the person that conducted the '
            'measurement.'
        )),
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
    )

    md_person_email = md_entry(
        name='person_email',
        required_field=True,
        required_lab=True,
        multiline=False,
        dublin_core=None,
        description='Email address of the person now '
        'maintaining this data set.',
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
    )

    md_attending_persons = md_entry(
        name='attending_persons',
        required_field=False,
        required_lab=False,
        multiline=False,
        dublin_core='contributor',
        description=''.join((
            'All persons that were involved during the measurement. '
            'Optional: Add email addresses in parentheses, '
            'e.g. Maximilian Weigand (mweigand@geo.uni-bonn.de)'
        )),
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
    )

    md_survey_start = md_entry(
        name='survey_start',
        required_field=False,
        required_lab=False,
        multiline=False,
        dublin_core=None,
        description=''.join((
            'Starting datetime of survey. '
            'Intended for the field data tree. '
            'Format: yyyymmdd hh:mm:ss'
        )),
        plevel=[dir_levels.datetime_group_field],
        data_type=str,
        allowed_values=None,
        conditions={
            md_survey_type: 'field',
        },
    )

    md_survey_end = md_entry(
        name='survey_end',
        required_field=False,
        required_lab=False,
        multiline=False,
        dublin_core=None,
        description=''.join((
            'Ending datetime of survey. '
            'Intended for the field data tree. '
            'Format: yyyymmdd hh:mm:ss (same as survey_start)'
        )),
        plevel=[dir_levels.datetime_group_field],
        data_type=str,
        allowed_values=None,
        conditions={
            md_survey_type: 'field',
        },
    )

    md_experiment_start = md_entry(
        name='experiment_start',
        required_field=False,
        required_lab=False,
        multiline=False,
        dublin_core=None,
        description=''.join((
            'Starting datetime of experiment. '
            'Intended for the laboratory data tree. '
            'Format: yyyymmdd hh:mm:ss'
        )),
        plevel=[dir_levels.datetime_group_lab],
        data_type=str,
        allowed_values=None,
        conditions={
            md_survey_type: 'laboratory',
        },
    )

    md_site_lab = md_entry(
        name='site',
        required_field=False,
        required_lab=True,
        multiline=False,
        dublin_core=None,
        description='Laboratory measurement site',
        plevel=dir_levels.site_lab,
        data_type=str,
        allowed_values=None,
        conditions={
            md_survey_type: 'laboratory',
        },
    )

    md_lab_group = md_entry(
        name='group',
        required_field=False,
        required_lab=False,
        multiline=False,
        dublin_core=None,
        description='High-level group of experiments',
        plevel=dir_levels.site_lab,
        data_type=str,
        allowed_values=None,
        conditions={
            md_survey_type: 'laboratory',
        },
    )

    md_experiment_end = md_entry(
        name='experiment_end',
        required_field=False,
        required_lab=False,
        multiline=False,
        dublin_core=None,
        description=''.join((
            'Ending datetime of experiment. '
            'Intended for the laboratory data tree. '
            'Format: yyyymmdd hh:mm:ss (same as experiment_start)'
        )),
        plevel=[dir_levels.datetime_group_lab],
        data_type=str,
        allowed_values=None,
        conditions={
            md_survey_type: 'laboratory',
        },
    )

    md_datetime_end = md_entry(
        # added because there was a datetime_start differing from plan
        name='datetime_end',
        required_field=False,
        required_lab=False,
        multiline=False,
        dublin_core='date',
        description='Ending datetime of the measurement/measurements',
        plevel=[
            dir_levels.datetime_group_field, dir_levels.datetime_group_lab],
        data_type=str,
        allowed_values=None,
    )

    md_dt_group = md_entry(
        name='dt_group',
        required_field=False,
        required_lab=False,
        dirtree_optional=True,
        multiline=False,
        dublin_core='',
        description='Datetime group -- Used to group measurements, '
        'e.g. into days or years',
        plevel=[
            dir_levels.datetime_group_field, dir_levels.datetime_group_lab],
        data_type=str,
        allowed_values=None,
    )

    md_project = md_entry(
        name='project',
        required_field=False,
        required_lab=False,
        multiline=False,
        dublin_core='part of title',
        description='?',
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
    )

    md_coordinates = md_entry(
        name='coordinates',
        required_field=False,
        required_lab=False,
        multiline=True,
        dublin_core=None,
        description=' '.join((
            'Coordinates of representative location(s)',
            '(i.e., starting point of measurement profile).',
            'One coordinate per line',
            'The use of WGS84 coordinates is preferred (EPSG 4326).',
            'Please state the use of other coordinate systems in the metadata',
            'entry "coordinates_desc".',
            'Coordinates should be included in decimal notation, with a least',
            '6 decimal digits (ca. 5-12cm precision).',
            '\n See',
            'https://wiki.openstreetmap.org/wiki/Precision_of_coordinates',
            '\n',
            '\nFormat: One coordinate per line. Either two or three columns,',
            'separated by the character ";".\n The first two columns always ',
            'are: latitude and longitude.\n',
            'An optional third column, "description" can hold',
            'identifiers, such as "start", "end", etc.\n',
            'A header column, starting with "#", is optional.\n',
            '\n\nExample:',
            '\n#lat;lon;description',
            '\n50.706019097;7.210912815;start',
        )),
        plevel=None,
        data_type=str,
        allowed_values=None,
        conditions={
            md_survey_type: 'field',
        },
    )

    md_coordinates_desc = md_entry(
        name='coordinates_desc',
        required_field=False,
        required_lab=False,
        multiline=True,
        dublin_core=None,
        description=' '.join((
            'Description of coordinates. State used representation '
            '(e.g., WGS84 or UTM) here. Do not forget the UTM zone',
        )),
        plevel=None,
        data_type=str,
        allowed_values=None,
        conditions={
            md_survey_type: 'field',
        },
    )
    md_keywords = md_entry(
        name='keywords',
        required_field=False,
        required_lab=False,
        multiline=False,
        dublin_core='subject',
        description='Keywords, separated by comma.',
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
    )

    md_theme_complex = md_entry(
        name='theme_complex',
        required_field=True,
        required_lab=True,
        multiline=False,
        dublin_core='subject',
        description=''.join((
            'Theme complex that the measurement falls under. ' +
            'This is the most general category for a given measurement'
        )),
        plevel=[dir_levels.theme_complex],
        data_type=str,
        allowed_values=None,
        # conditions={
        #     md_survey_type: 'laboratory',
        # },
        autocomplete=[
            'Biogeophysics',
            'Cryogeophysics',
            'TestMeasurements',
        ],
    )

    md_description_exp = md_entry(
        name='description_exp',
        required_field=False,
        required_lab=False,
        multiline=True,
        dublin_core=None,
        description=''.join((
            'Description (should be short, comprehensive, and link to '
            'detailed documentation)'
        )),
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
    )

    md_related_dois = md_entry(
        name='related_dois',
        required_field=False,
        required_lab=False,
        multiline=True,
        dublin_core='references',
        description='',
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
    )

    md_analysis_links = md_entry(
        name='analysis_links',
        required_field=False,
        required_lab=False,
        multiline=True,
        dublin_core=None,
        description='?',
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
    )

    md_problems = md_entry(
        name='problems',
        required_field=False,
        required_lab=False,
        multiline=True,
        dublin_core=None,
        description=''.join((
            'Known restrictions/problems of the dataset '
            '(entries should be time stamped, multi-line entries required)'
        )),
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
    )

    md_missing = md_entry(
        name='missing',
        required_field=False,
        required_lab=False,
        multiline=True,
        dublin_core=None,
        description='?',
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
    )

    md_signed_off_by = md_entry(
        name='signed_off_by',
        required_field=False,
        required_lab=False,
        multiline=True,
        dublin_core=None,
        description='?',
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
    )

    # section: [device]

    md_device = md_entry(
        name='device',
        required_field=False,
        required_lab=False,
        multiline=False,
        dublin_core=None,
        description='Used measurement instrument.',
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
        autocomplete=[
            'IRIS Syscal Pro',
            'FZJ Medusa',
            'FZJ SIP04',
            'Datataker DT80 Series 3',
            'Datataker DT80 Series 4',
            'Fluke Voltmeter',
        ],
    )

    md_device_serial = md_entry(
        name='device_serial',
        required_field=False,
        required_lab=False,
        multiline=False,
        dublin_core=None,
        description=''.join((
            'Serial number of instrument, required if several devices of '
            'one type exist (e.g. the DT80)'
        )),
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
    )

    md_programming = md_entry(
        name='programming',
        required_field=False,
        required_lab=False,
        multiline=False,
        dublin_core=None,
        description=''.join((
            'Optional file path to a script/file containing the '
            'programming (script) used for the measurements(s)'
        )),
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
    )

    # section: [sample]

    md_specimen = md_entry(
        name='specimen',
        required_field=False,
        required_lab=False,
        multiline=False,
        dublin_core=None,
        description=''.join((
            'Sample material, e.g. sandstone; '
            'used mainly for laboratory measurement metadata.'
        )),
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
        conditions={
            md_survey_type: 'laboratory',
        },
    )

    md_porosity = md_entry(
        name='porosity',
        required_field=False,
        required_lab=False,
        multiline=False,
        dublin_core=None,
        description='Porosity of sample material',
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
        conditions={
            md_survey_type: 'laboratory',
        },
    )

    md_permeability = md_entry(
        name='permeability',
        required_field=False,
        required_lab=False,
        multiline=False,
        dublin_core=None,
        description='Permeability of sample material',
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
        conditions={
            md_survey_type: 'laboratory',
        },
    )

    # section: [ert] # (device specific info NOT always contained in raw data)

    md_spacing = md_entry(
        name='spacing',
        required_field=False,
        required_lab=False,
        multiline=False,
        dublin_core=None,
        description='Electrode spacing',
        plevel=[dir_levels.measurement_field, dir_levels.measurement_lab],
        data_type=str,
        allowed_values=None,
    )

    md_ert_profile_direction = md_entry(
        name='profile_direction',
        required_field=True,
        required_lab=False,
        multiline=False,
        dublin_core=None,
        description='Profile direction. Allowed values: normal, reciprocal',
        plevel=[dir_levels.measurement_field, ],
        data_type=str,
        allowed_values=['normal', 'reciprocal'],
        conditions={
            md_survey_type: 'field',
            md_method: ('IP', 'EIT', 'ERT'),
        },
    )

    md_ert_electrode_positions = md_entry(
        name='electrode_positions',
        required_field=True,
        required_lab=False,
        multiline=True,
        dublin_core=None,
        description='Electrode positions (x,y,z)',
        plevel=[dir_levels.measurement_field, ],
        data_type=str,
        allowed_values=None,
        conditions={
            md_survey_type: 'field',
            md_method: ('IP', 'EIT', 'ERT'),
        },
        autocomplete=[
            'ERT',
            'TDIP',
            'SP',
            'GPS',
            'GPR',
            'EMI',
            'TDEM',
            'Seismics',
        ],
    )

    # define the actual meta data structure here
    md_entries = {
        'general': {
            md_label.name: md_label,
            md_person_responsible.name: md_person_responsible,
            md_person_email.name: md_person_email,
            md_attending_persons.name: md_attending_persons,
            md_theme_complex.name: md_theme_complex,
            md_project.name: md_project,
            md_datetime_start.name: md_datetime_start,
            md_datetime_end.name: md_datetime_end,
            md_description.name: md_description,
            md_survey_type.name: md_survey_type,
            md_method.name: md_method,
            md_experiment.name: md_experiment,
            md_description_exp.name: md_description_exp,
            md_restrictions.name: md_restrictions,
            md_completed.name: md_completed,
            md_keywords.name: md_keywords,
            md_related_dois.name: md_related_dois,
            md_missing.name: md_missing,
            md_problems.name: md_problems,
            md_signed_off_by.name: md_signed_off_by,
            md_analysis_links.name: md_analysis_links,
            md_dt_group.name: md_dt_group,
        },
        'field': {
            md_survey_start.name: md_survey_start,
            md_survey_end.name: md_survey_end,
            md_site.name: md_site,
            md_area.name: md_area,
            md_profile.name: md_profile,
            md_coordinates.name: md_coordinates,
            md_coordinates_desc.name: md_coordinates_desc,
        },
        'geoelectrics': {
            md_spacing.name: md_spacing,
            md_ert_profile_direction.name: md_ert_profile_direction,
            md_ert_electrode_positions.name: md_ert_electrode_positions,
        },
        'laboratory': {
            md_site_lab.name: md_site_lab,
            md_lab_group.name: md_lab_group,
            md_experiment_start.name: md_experiment_start,
            md_experiment_end.name: md_experiment_end,
            md_specimen.name: md_specimen,
            md_permeability.name: md_permeability,
            md_porosity.name: md_porosity,
        },
        'device': {
            md_device.name: md_device,
            md_device_serial.name: md_device_serial,
            md_programming.name: md_programming,
        },
    }

    return metadata_tree(md_entries)


def get_empty_metadata_tree():
    """Return an empty metadata tree"""
    md_tree = get_md_values()
    return md_tree


def export_metadata_to_latex():
    """Export the metadata structure as a Latex table

    Work in Progress !!!
    """
    str_lines = []
    str_lines.append(r'\begin{longtable}{c|c|c|c|c|p{6cm}}')
    str_lines.append(
        r'key & multi-line & required field & required lab &' +
        r'Doublin Core & description\\'
    )

    mentries = get_md_values()
    for section, item in mentries.items():
        str_lines.append(r'\hline')
        str_lines.append(r'section: [{}]\\'.format(section))
        str_lines.append(r'\hline')

        for name, entry in item.items():
            if entry.multiline:
                multiline = r'\faCheck'
            else:
                # multiline = 'n'
                multiline = r'\faTimes'

            if entry.dublin_core is None:
                dc = ''
            else:
                dc = entry.dublin_core
            str_lines.append(
                r'{} & {} & {} & {} & {} & {} \\'.format(
                    name,
                    multiline,
                    entry.required_field,
                    entry.required_lab,
                    dc,
                    entry.description
                ).replace('_', r'\_').replace('%', r'\%')
            )

    str_lines.append(r'\end{longtable}')
    return "\n".join(str_lines)


def export_metadata_descriptions_to_file(filename):
    md_descriptions = export_metadata_to_latex()
    with open(filename, 'w') as fid:
        fid.write(md_descriptions)
