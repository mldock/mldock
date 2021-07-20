"""PLATFORM HELPERS MLDOCK UTILITIES"""
import json

def _format_key_as_mldock_env_var(key, prefix=None):
    """
        Formats key as mldock env variable.
        Replace ' ' and '-', append mldock prefix
        and lastly transforms to uppercase
    """
    if prefix is not None:
        if not key.lower().startswith(prefix.lower()):
            key = "{PREFIX}_{KEY}".format(PREFIX=prefix, KEY=key)

    key = key.replace(" ", "_").replace("-", "_")
    key = key.upper()
    return key

def _format_dictionary_as_env_vars(obj: dict, group=None):
    """
        format key and values as appropriate environment variables

        namely:
            - upper case
            - replace spaces with "_"
            - replace dashes with "_"
            - add owner prefix
    """
    new_keys = {}
    for _key,_value in obj.items():

        _key = _format_key_as_mldock_env_var(_key, prefix=group)

        if isinstance(_value, dict):
            _value = json.dumps(_value)

        new_keys.update(
            {
                _key: _value
            }
        )
    return new_keys

def collect_mldock_environment_variables(**env_vars):
    """Collect and format mldock environment variables"""
    return _format_dictionary_as_env_vars(
        env_vars,
        group='mldock'
    )

def _make_sagemaker_input_data_configs(data_channels: list):
    """restructures a list of data names as sagemaker input data configs"""
    return {name: {} for name in data_channels}

def _extract_data_channels_from_mldock(mldock_data: list):

    data_channels = [
        data_config['channel'] for data_config in mldock_data
    ]

    return _make_sagemaker_input_data_configs(data_channels=data_channels)
