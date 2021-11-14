"""Logger formatter"""
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import sys
import logging
import click

PY2 = sys.version_info[0] == 2


class ColorFormatter(logging.Formatter):
    """ColorFormatter for logging.Logger"""

    colors = {
        "error": dict(fg="red"),
        "exception": dict(fg="red"),
        "critical": dict(fg="red"),
        "debug": dict(fg="blue"),
        "warning": dict(fg="yellow"),
    }

    def format(self, record):
        """format record method"""
        if not record.exc_info:
            level = record.levelname.lower()
            msg = record.msg
            if level in self.colors:
                prefix = click.style("{}: ".format(level), **self.colors[level])
                if not PY2 and isinstance(msg, bytes):
                    msg = msg.decode(sys.getfilesystemencoding(), "replace")
                elif not isinstance(msg, (str, bytes)):
                    msg = str(msg)
                msg = "\n".join(prefix + x for x in msg.splitlines())
            return msg
        return logging.Formatter.format(self, record)


class ClickHandler(logging.Handler):
    """Click log format handler based on logging.Handler"""

    def emit(self, record):
        """log record emitter"""
        # pylint: disable=broad-except
        try:
            msg = self.format(record)
            level = record.levelname.lower()
            err = level in ("warning", "error", "exception", "critical")
            click.echo(msg, err=err)
        except Exception:
            self.handleError(record)


def _normalize_logger(logger, log_level):
    """normalize logger based on log_level."""
    if not isinstance(logger, logging.Logger):
        logger = logging.getLogger(logger)

    logger.setLevel(log_level)
    return logger


def configure_logger(logger, verbose=False):
    """configure a new logger in either DEBUG or INFO based on verbose flag."""
    log_level = logging.DEBUG if verbose else logging.INFO

    logger = _normalize_logger(logger, log_level)
    _default_handler = ClickHandler()
    _default_handler.formatter = ColorFormatter()
    logger.handlers = [_default_handler]
    logger.propagate = False
    return logger
