"""
Provide means to interactively set metadata entries

The cache concept:

    One problem we face is how to merge information we have on the data from
    different sources, such as:

    * existing metadata files
    * filenames
    * file types
    * previous entries

Our current approach is to basically gather all this information an put it into
a cache object that is used for auto-completion during input, and select one of
the inputs as a default value that can simply be accepted by the user.

Thoughts on how to incorporate non-essential metadata entries:

    I think on the lower levels we need a state machine that can go through the
    essential metadata entries, but can also jump to non-essential entries, if
    requested by the user.

Thoughts/todo items on metadata entries:

    * How to add non-required directory levels?

I think we need multiple bits of information for each metadata entry:

    * required entry?
    * optional for directory structure (in contrast to: optional for metadatas)

Ask for user input in the following order:

    1) required metadata entries
    2) optional entries for directory structure (i.e., group/experiment/etc.)
    3) additional entries

"""
from ubg_data_toolbox.metadata_definitions import get_md_values
# from ubg_data_toolbox.dirtree import tree

from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit import print_formatted_text, HTML


bindings = KeyBindings()


@bindings.add('c-a')
def _(event):
    b = event.app.current_buffer
    # document = b.document
    b.delete_before_cursor(100)


@bindings.add('c-u')
def _(event):
    # move backwards
    event.app.direction = -1
    # we do not want to commit the current buffer content
    event.app.exit()


# this is just an alternative to ALT-ENTER for ending multi-line input
# we had some problems on MAC systems
@bindings.add('c-e')
def _(event):
    # commit the current buffer
    event.app.current_buffer.validate_and_handle()


@bindings.add('c-z')
def _(event):
    # do we allow ending here?
    if event.app.no_end_now:
        # do noting
        return
    # move backwards
    event.app.end_now = True
    # commit the current buffer
    event.app.current_buffer.validate_and_handle()


def get_default_value(entry, cache_default_values):
    """
    Determine a default value for metadata input.

    At this point there are only two possibilities: Either there was a previous
    entry for the metadata entry (in this session), or the default value is
    used.
    """
    if entry.value is not None or entry.value != '':
        default_value = cache_default_values.get(entry.name)
    else:
        default_value = entry.value
    if default_value is None:
        default_value = ''

    return default_value


def ask_user_for_metadata(
        md_entries=None, ask_for='required', show_menu=False, **kwargs):
    """

    TODO: honor "conditions"
    TODO: add the possibility to ask for the value to change

    Parameters
    ----------
    md_entries :
        this is the metadata structure to be filled. If None, create a new
        (empty one) and work with the default entries
    ask_for: str
        required|dirtree_optional|optional

    Other Parameters
    ----------------

    """
    # used for default values
    cache_default_values = kwargs.get('cache_default_values',)

    if md_entries is None:
        # start fresh with an empty metadata set
        md_entries = get_md_values()

    def ask(section, entry, no_end_now=False):
        """Prompt for input

        Returns
        -------
        input_text: str|None
            The returned input string
        direction: int
            +1 or -1: the direction in which we want to proceed
        stop_now: bool
            If True, then this indicates that the used want to stop the current
            editing loop
        """
        if entry.allowed_values is not None:

            def in_list(text):
                return text in entry.allowed_values

            validator = Validator.from_callable(
                in_list,
                error_message='Only the following values are '
                'allowed: {}'.format(entry.allowed_values),
                move_cursor_to_end=True
            )
            history = InMemoryHistory()
            for word in entry.allowed_values:
                history.append_string(word)
            allowed_value_completer = WordCompleter(
                entry.allowed_values,
                match_middle=True,
            )
        else:
            validator = None
            if entry.autocomplete is not None:
                assert isinstance(entry.autocomplete, list)
                history = InMemoryHistory()
                for word in entry.autocomplete:
                    history.append_string(word)

                allowed_value_completer = WordCompleter(
                    entry.autocomplete,
                    match_middle=True,
                )
            else:
                history = None
                allowed_value_completer = None

        session = PromptSession(
            history=history,
            auto_suggest=AutoSuggestFromHistory(),
            enable_history_search=True,
            completer=allowed_value_completer,
            complete_while_typing=True,
            key_bindings=bindings,
        )
        # we use this custom variables to extract information out of the
        # key bindings (see at the top of the file)
        session.app.direction = 1
        session.app.end_now = False
        session.app.no_end_now = no_end_now

        msg = 'Enter value for {}.{}: '.format(section, entry.name)
        # if not entry.required:
        #     msg = '(optional) ' + msg

        default_value = get_default_value(entry, cache_default_values)
        info_text = [
            # '',
            HTML('<ansigreen>' + 80 * '-' + '</ansigreen>'),
            HTML('Delete last 100 characters: <b>STRG - a</b>'),
            HTML('Ignore current input and go backwards: <b>STRG - u</b>'),
        ]

        if not no_end_now:
            info_text += [
                HTML(
                    'Commit current input and stop data input <b>STRG - z</b>'
                ),
            ]

        if entry.multiline:
            info_text = info_text + [
                HTML('This is a <b>multiline</b> input'),
                HTML('End input using <b>ALT - ENTER</b> or <b>STRG - e</b>'),
            ]
        else:
            pass
            # info_text = ['', ]

        if history is not None:
            info_text = info_text + [
                HTML('There are autocomplete values available (Press TAB).'),
            ]
        else:
            pass
            # info_text = ['', ]

        info_text.append(HTML(
            '<ansigreen>' + 80 * '-' + '</ansigreen>')
        )

        for line in info_text:
            print_formatted_text(line)

        def prompt_continuation(width, line_number, is_soft_wrap):
            return '.' * (width - 1) + ' '

        # show description
        print_formatted_text(HTML(
            '<div bg="gray">' +
            entry.description +
            '</div>'
        ))

        # actually ask for input
        input_text = session.prompt(
            msg,
            validator=validator,
            # bottom_toolbar=entry.description,
            default=default_value,
            multiline=entry.multiline,
            prompt_continuation=prompt_continuation,
        )
        print_formatted_text(
            HTML('<ansigreen>' + 80 * '-' + '</ansigreen>')
        )
        # return input_text, 1, False
        return input_text, session.app.direction, session.app.end_now

    # we always need to know the survey type
    entry = md_entries['general']['survey_type']

    # only ask if we want to recheck or do not have any information
    if ask_for == 'required' or entry.is_empty():
        input_text, _, _ = ask('general', entry)

        # retain input for next time
        cache_default_values.set(entry.name, input_text)
        entry.value = input_text

    # IPython.embed()
    if entry.value == 'field':
        key_required = 'required_field'
    else:
        key_required = 'required_lab'

    if show_menu:
        # use a menu-loop to selectively set values

        # build up a selection dict
        editable_entries = {}
        index = 0

        for section in md_entries.keys():
            for entry in md_entries[section].values():
                # check if this entry is of the type we want to ask for
                if ask_for == 'required' and not getattr(entry, key_required):
                    continue
                if (ask_for == 'dirtree_optional' and
                   not entry.dirtree_optional):
                    continue
                if ask_for == 'optional' and (
                        getattr(
                            entry, key_required) or entry.dirtree_optional):
                    continue
                # check conditions
                if entry.conditions is not None:
                    conditions_met = True
                    for subentry, required_value in entry.conditions.items():
                        if subentry.value != required_value:
                            conditions_met = False
                    if not conditions_met:
                        continue
                editable_entries[index] = (section, entry.name, entry)
                index += 1

        # show the menu
        exit_menu = False
        while not exit_menu:
            for key, item in sorted(editable_entries.items()):
                entry = item[2]

                # index number
                line = '{:>2} - '.format(key)
                # section.name
                line += '{:>10}.{:<18} - '.format(item[0], entry.name)
                # value
                if entry.value is not None:
                    color = 'green'
                    line += '{:>20}'.format(entry.value)
                else:
                    color = 'red'
                    line += ' ' * 20
                # description
                # line += ' - {}'.format(entry.description)

                # add colors
                line = '<{0}>{1}</{0}>'.format(color, line)
                print_formatted_text(HTML(line))

            print('')
            print('Type f / finish to exit this menu')
            menu_selection = prompt('Enter nr to edit:')
            if menu_selection in ('f', 'finish'):
                exit_menu = True
                continue
            # TODO: add validation
            md_number = int(menu_selection)
            input_text, _, _ = ask(
                section=editable_entries[md_number][0],
                entry=editable_entries[md_number][2],
            )
            # retain input for next time
            cache_default_values.set(
                editable_entries[md_number][1],
                input_text
            )
            editable_entries[md_number][2].value = input_text
    else:
        # print('CYCLING')
        # import IPython
        # IPython.embed()
        # build up a list of (potentially) askable entries
        entry_list = []
        for section in md_entries.keys():
            for entry in md_entries[section].values():
                # we do not want to ask for all entries, filter those that we
                # do not want here
                if section == 'general' and entry.name == 'survey_type':
                    # skip because we already asked this at the beginning
                    continue
                if ask_for == 'required' and not getattr(entry, key_required):
                    continue
                if (ask_for == 'dirtree_optional' and
                        not entry.dirtree_optional):
                    continue
                if ask_for == 'optional' and (
                        getattr(
                            entry, key_required) or entry.dirtree_optional):
                    continue

                entry_list += [(section, entry)]

        # this is the number of items that we want information on
        nr_items = len(entry_list)

        direction = 1
        # this is the index of the entry that will get asked next
        next_index = 0
        while next_index < nr_items:
            section, entry = entry_list[next_index]

            # check if we need to honor conditions
            if not entry.conditions_are_met():
                # do nothing, we ignore this entry
                pass
            else:
                input_text, direction, end_now = ask(
                    section,
                    entry,
                    # it does not make sense to provide a short-cut to skip
                    # entries
                    no_end_now=True,
                )

                # retain input for next time
                if input_text is not None:
                    cache_default_values.set(entry.name, input_text)
                    entry.value = input_text

            next_index += direction

        # # just cycle through all entries
        # for section in md_entries.keys():
        #     for entry in md_entries[section].values():
        #         if section == 'general' and entry.name == 'survey_type':
        #             # skip because we already asked this at the beginning
        #             continue
        #         # check if this entry is of the type we want to ask for
        #         if ask_for == 'required' and not getattr(entry,
        #                key_required):
        #             continue
        #         if (ask_for == 'dirtree_optional' and
        #                 not entry.dirtree_optional):
        #             continue
        #         if ask_for == 'optional' and (
        #                 getattr(
        #                     entry, key_required) or entry.dirtree_optional):
        #             continue
        #         # print('        Getting value from user')

        #         input_text = ask(section, entry)
        #         # retain input for next time
        #         cache_default_values.set(entry.name, input_text)
        #         entry.value = input_text

    return md_entries
