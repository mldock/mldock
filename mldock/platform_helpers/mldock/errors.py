"""PLATFORM HELPERS MLDOCK ERRORS"""
import sys
import traceback


def extract_stack_trace() -> str:
    """Extracts full stacktrace from thown exception
    Returns:
        str: traceback of error thrown
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    stack_trace = traceback.format_exception(exc_type, exc_value, exc_traceback)
    return repr(stack_trace)
