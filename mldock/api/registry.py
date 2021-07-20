"""Registry API methods"""
import logging
import click
import docker

logger=logging.getLogger('mldock')

def compute_progress(current, max_value=10):

    if current > max_value:
        multiple = current // max_value
        current = current - max_value * multiple

    return current

def get_layer_state(
    stream,
    layer_id,
    state={},
    progress='',
    fill_char='=',
    increment=2,
    max_value=40,
    status_tag='pushing'
):
    """
        Computes a status update to the state of layer during a push.
        Additionally, adds a progress bar and flexible fill character.
    """
    try:

        if status_tag.lower() == 'pushing':
            progress = ''
            if stream.lower() == status_tag.lower():
                current_layer = state[layer_id]
                current_progress = current_layer['progress'].replace("[",'').replace("]",'').replace(">",'')
                current_progress = len(current_progress)
                progress = compute_progress(current_progress, max_value=max_value) + increment
                progress = fill_char * progress
                progress = "[{}>]".format(progress)

        state.update(
            {layer_id: {'message':stream, 'progress': progress}}
        )
    except KeyError as exception:
        pass

    return state

def stateful_log_emitter(line: dict, status_tag: str, states={}):
    error = line.get('error', None)
    errorDetail = line.get('errorDetail', None)
    if error is not None:
        logger.error('{}\n{}'.format(error, errorDetail))
    
    stream = line.get('status','')
    layer_id = line.get('id','')
    progress = line.get('progress','')

    if (layer_id == ''):
        return states
    else:
        # perform status update, using layer_id as key
        states = get_layer_state(stream, layer_id, states, progress=progress, status_tag=status_tag)

        # clear terminal to allow for friendlier update
        click.clear()

        # emit current state to stdout
        {logger.info("{}: {} {}".format(k,v['message'], v['progress'])) for k, v in states.items()}

    return states

def push_image_to_repository(
    image_repository: str,
    auth_config: dict,
    tag='latest'
):
    """
        Push image to repository in registry. Using auth_config this will Authenticate client.
    """
    client = docker.from_env()

    push_response = client.images.push(
        repository=image_repository,
        tag=tag,
        stream=True,
        decode=True,
        auth_config=auth_config
    )

    states = {}
    for line in push_response:
        states = stateful_log_emitter(line=line, states=states, status_tag='Pushing')
    return states

def pull_image_from_repository(
    image_repository: str,
    auth_config: dict,
    tag='latest'
):
    """
        Pull image from repository in registry. Using auth_config this will Authenticate client.
    """
    client = docker.from_env()

    pull_response = client.api.pull(
        repository=image_repository,
        tag=tag,
        stream=True,
        decode=True,
        auth_config=auth_config
    )

    states = {}
    for line in pull_response:
        states = stateful_log_emitter(line=line, states=states, status_tag='Downloading')
    return states
