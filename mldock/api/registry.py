"""Registry API methods"""
import logging
import click
import docker

logger = logging.getLogger("mldock")


def compute_progress(current, max_value=10):
    """
    compute the progress bar update

    args:
        current (int): current count of progress bar
        max_value (int): (default=10) maximum length of progress bar
    returns:
        (int): updated progress bar
    """
    if current > max_value:
        multiple = current // max_value
        current = current - max_value * multiple

    return current


def get_layer_state(stream: str, layer_id: str, state: dict = None, **kwargs):
    """
    Computes a status update to the state of layer during a push.
    Additionally, adds a progress bar and flexible fill character.

    args:
        stream (str): stream message
        layer_id (str): stream layer id
        state (dict) (default=None) current state
    kwargs:
        progress (str): (default = '') starting progress bar string
        fill_char (str): (default='=') fill char to use as progress bar
        increment (str): (default=2) progress bar char increment to use
        max_value (str): (default=40) maximum progress bar length
        status_tag (str): (default='pushing') key to use to look for updates
    """
    progress = kwargs.get("progress", "")
    fill_char = kwargs.get("fill_char", "=")
    increment = kwargs.get("increment", 2)
    max_value = kwargs.get("max_value", 40)
    status_tag = kwargs.get("status_tag", "pushing")

    try:

        if status_tag.lower() == "pushing":
            # progress = ''
            if stream.lower() == status_tag.lower():
                current_layer = state[layer_id]
                current_progress = (
                    current_layer["progress"]
                    .replace("[", "")
                    .replace("]", "")
                    .replace(">", "")
                )
                current_progress = len(current_progress)
                progress = (
                    compute_progress(current_progress, max_value=max_value) + increment
                )
                progress = fill_char * progress
                progress = "[{}>]".format(progress)

        state.update({layer_id: {"message": stream, "progress": progress}})
    except KeyError:
        pass

    return state


def stateful_log_emitter(line: dict, status_tag: str, states: dict = None):
    """
    stateful log emitter

    args:
        line (dict): current record of logs
        status_tag (str): key to use to update state
        states (dict): current state of logs
    """
    if states is None:
        states = {}

    error = line.get("error", None)
    error_detail = line.get("errorDetail", None)
    if error is not None:
        logger.error("{}\n{}".format(error, error_detail))

    stream = line.get("status", "")
    layer_id = line.get("id", "")
    progress = line.get("progress", "")

    # perform status update, using layer_id as key
    states = get_layer_state(
        stream, layer_id, states, progress=progress, status_tag=status_tag
    )

    # clear terminal to allow for friendlier update
    click.clear()

    # emit current state to stdout
    for key, value in states.items():
        logger.info(
            "{KEY}: {MESSAGE} {PROGRESS}".format(
                KEY=key, MESSAGE=value["message"], PROGRESS=value["progress"]
            )
        )

    return states


def push_image_to_repository(image_repository: str, auth_config: dict, tag="latest"):
    """
    Push image to repository in registry. Using auth_config this will Authenticate client.
    """
    client = docker.from_env()

    push_response = client.images.push(
        repository=image_repository,
        tag=tag,
        stream=True,
        decode=True,
        auth_config=auth_config,
    )

    states = {}
    for line in push_response:
        states = stateful_log_emitter(line=line, states=states, status_tag="Pushing")
    return states

def tag_image(current_repository, new_repository, new_tag):
    client = docker.from_env()
    client.api.tag(current_repository, repository=new_repository, tag=new_tag, force=False)
    return f"{new_repository}:{new_tag}"


def pull_image_from_repository(image_repository: str, auth_config: dict, tag="latest"):
    """
    Pull image from repository in registry. Using auth_config this will Authenticate client.
    """
    client = docker.from_env()

    pull_response = client.api.pull(
        repository=image_repository,
        tag=tag,
        stream=True,
        decode=True,
        auth_config=auth_config,
    )

    states = {}
    for line in pull_response:
        states = stateful_log_emitter(
            line=line, states=states, status_tag="Downloading"
        )
    
    return states

