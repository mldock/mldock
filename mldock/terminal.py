"""
    Terminal Utils

    Incl. styling and formatting in terminal commands.
"""
import logging
import click
import typing as t
from gettext import ngettext
from halo import Halo

logger = logging.getLogger('mldock')

def pretty_build_logs(line: dict):

    if line is None:
        return None

    error = line.get('error', None)
    errorDetail = line.get('errorDetail', None)

    if error is not None:
        logger.error('{}\n{}'.format(error, errorDetail))
    
    stream = line.get('stream', '')

    return " ==> {MESSAGE}".format(MESSAGE=stream)

class ProgressLogger:
    """
        A terminal based progress context manager.

        starts the progress spinner, and passes the object back.
        finally raises success or failure if exception is raised.    
    """
    def __init__(self, **kwargs):
        self.group = kwargs.pop('group', None)
        if self.group is None:
            self.group = kwargs.get('text', None)

        self.on_success = kwargs.pop('on_success', None)
        self.on_failure = kwargs.pop('on_failure', None)
        
        if len(self.group) > 0:
            self.group = self.group + " "

        self.spinner = Halo(**kwargs)

    def __enter__(self):
        self.spinner.start()
        return self.spinner

    def __exit__(self, exc_type, exc_value, exc_tb):
        # all though this always runs on complete
        # we would like behaviour to register either success or failure
        # use exc_type == None to raise success
        if exc_type is not None:
            error_msg = "Error raised during {}".format(self.group)
            if self.on_failure is not None:
                error_msg = self.on_failure
            self.spinner.fail(error_msg)
            return False # reraise the exception

        success_msg = "{}Complete".format(self.group)
        if self.on_success is not None:
            success_msg = self.on_success
        self.spinner.succeed(success_msg)
        return True

class ChoiceWithNumbers(click.Choice):
    """Extends the click.Choice class to allow user to make choice by number"""
    def convert(
        self, value: t.Any, param: t.Optional["Parameter"], ctx: t.Optional["Context"]
    ) -> t.Any:
        """
            Match through normalization and case sensitivity
            first do token_normalize_func, then lowercase
            preserve original `value` to produce an accurate message in
            `self.fail`
        """
        normed_value = value
        normed_choices = {choice: choice for choice in self.choices}
        try:
            # try coherse to integer else
            normed_value = int(normed_value)
            normed_value = self.choices[normed_value - 1]

        except Exception as exception:
            pass

        if ctx is not None and ctx.token_normalize_func is not None:
            normed_value = ctx.token_normalize_func(value)
            normed_choices = {
                ctx.token_normalize_func(normed_choice): original
                for normed_choice, original in normed_choices.items()
            }

        if not self.case_sensitive:
            normed_value = normed_value.casefold()
            normed_choices = {
                normed_choice.casefold(): original
                for normed_choice, original in normed_choices.items()
            }

        if normed_value in normed_choices:
            return normed_choices[normed_value]

        choices_str = ", ".join(map(repr, self.choices))
        self.fail(
            ngettext(
                "{value!r} is not {choice}.",
                "{value!r} is not one of {choices}.",
                len(self.choices),
            ).format(value=value, choice=choices_str, choices=choices_str),
            param,
            ctx,
        )

def style_2_level_detail(major_detail, minor_detail):
    """Styling for two level detail"""
    format_minor_detail = click.style(
        "({})".format(minor_detail),
        fg='bright_green'
    )
    return "{} {}".format(
        major_detail,
        format_minor_detail
    )

def style_dropdown(group_name: str, options: list, default: str = None):
    """Styling prompt with choice options as a drop down list"""
    options = options.copy()
    for i, option in enumerate(options):
        option_formatted = "[{id}] {option}".format(id=i+1, option=option)
        if option == default:
            option_formatted = click.style(option_formatted, fg='bright_blue')
        options[i] = option_formatted

    option_msg = "\n".join(options)
    return "(Select {group_name} from list)\n\n{option_msg}\n=>".format(
        group_name=click.style(group_name, fg='bright_blue'),
        option_msg=option_msg
    )
