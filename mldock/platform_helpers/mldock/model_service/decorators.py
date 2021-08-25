from functools import wraps
import os
import traceback

def make_decorator(foreign_decorator):
    """
        Returns a copy of foreignDecorator, which is identical in every
        way(*), except also appends a .decorator property to the callable it
        spits out.
    """
    def new_decorator(func):
        # Call to newDecorator(method)
        # Exactly like old decorator, but output keeps track of what decorated it
        R = foreign_decorator(func) # apply foreignDecorator, like call to foreignDecorator(method) would have done
        R.decorator = new_decorator # keep track of decorator
        #R.original = func         # might as well keep track of everything!
        return R

    new_decorator.__name__ = foreign_decorator.__name__
    new_decorator.__doc__ = foreign_decorator.__doc__
    # (*)We can be somewhat "hygienic", but newDecorator still isn't signature-preserving, i.e. you will not be able to get a runtime list of parameters. For that, you need hackish libraries...but in this case, the only argument is func, so it's not a big issue

    return new_decorator

def trainer(container, environment, logger):
    """
        Args:
            TrainingContainer, environment, logger
    """
    def general_decorator(function):

        @wraps(function)
        def func_wrapper(*args, **kwargs):
            """
                Wrapper function to decorate function

                This could be train.py:
            """
            training = container(environment=environment)
            try:
                training.startup()

                function(*args, **kwargs)
            except Exception as exception:
                # Write out an error file. This will be returned as the failureReason in the
                # DescribeTrainingJob result.
                trc = traceback.format_exc()
                log_file_path = os.path.join(environment.output_data_dir, 'failure')
                with open(log_file_path, 'w') as s:
                    s.write('Exception during training: ' + str(exception) + '\n' + trc)
                # Printing this causes the exception to be in the training job logs, as well.
                logger.error('Exception during training: ' + str(exception) + '\n' + trc)
                raise
            finally:
                training.cleanup()

        return func_wrapper

    # add doc and decorator metadata
    general_decorator = make_decorator(general_decorator)
    return general_decorator

def predictor(container, environment, logger):
    """
        Args:
            TrainingContainer, environment, logger

        note:
            - this is called each time server calls your method, now decorated with this.
    """
    def general_decorator(function):

        @wraps(function)
        def func_wrapper(*args, **kwargs):
            """
                Wrapper function to decorate function

                This could be train.py:
            """
            serving = container(environment=environment)
            try:
                serving.startup_worker()

                return function(*args, **kwargs)
            except Exception as exception:
                # Write out an error file. This will be returned as the failureReason in the
                # DescribeTrainingJob result.
                trc = traceback.format_exc()
                log_file_path = os.path.join(environment.output_data_dir, 'failure')
                with open(log_file_path, 'w') as s:
                    s.write('Exception during training: ' + str(exception) + '\n' + trc)
                # Printing this causes the exception to be in the training job logs, as well.
                logger.error('Exception during training: ' + str(exception) + '\n' + trc)
                raise
            finally:
                serving.cleanup_worker()

        return func_wrapper

    # add doc and decorator metadata
    general_decorator = make_decorator(general_decorator)
    return general_decorator
