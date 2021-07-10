from mldock.platform_helpers.mldock.utils import \
    _format_dictionary_as_env_vars, _format_key_as_mldock_env_var, \
        collect_mldock_environment_variables

class TestUtils:

    sample_environment = {
        "run_id": 2,
        "A_DUMMY_CONDITIONAL": True
    }

    sample_hyperparameters = {
        'hyperparameters': {
            "factors": 10,
            "Alpha criterion": 'gini',
            "weighting": {'A': 10, 'C': 2}
        }
    }

    sample_hyperparameter_validation = {'MLDOCK_HYPERPARAMETERS': '{"factors": 10, "Alpha criterion": "gini", "weighting": {"A": 10, "C": 2}}'}

    sample_collected_mldock_env_vars = {'MLDOCK_ENVIRONMENT': '{"run_id": 2, "A_DUMMY_CONDITIONAL": true}', 'MLDOCK_HYPERPARAMETERS': '{"factors": 10, "Alpha criterion": "gini", "weighting": {"A": 10, "C": 2}}', 'MLDOCK_STAGE': 'dev'}

    @staticmethod
    def test_format_key_as_mldock_env_var():
        """test format key for environment vars"""

        result = _format_key_as_mldock_env_var(
            key='run_id',
            prefix='mldock'
        )

        assert result == 'MLDOCK_RUN_ID', (
            "Failed, Keys were not in MLDOCK format"
        )

    @staticmethod
    def test_format_key_as_mldock_env_var_skips_where_already_prefixed():
        """test format key for environment vars"""

        result = _format_key_as_mldock_env_var(
            key='mldock_run_id',
            prefix='mldock'
        )

        assert result == 'MLDOCK_RUN_ID', (
            "Failed, Keys were not in MLDOCK format"
        )

    @staticmethod
    def test_format_key_as_mldock_env_var_handles_none_correctly():
        """test format key for environment vars"""

        result = _format_key_as_mldock_env_var(
            key='run_id',
            prefix=None
        )

        assert result == 'RUN_ID', (
            "Failed, Keys were not in MLDOCK format"
        )

    def test_format_dictionary_as_env_vars(self):
        """test format key for environment vars"""

        result = _format_dictionary_as_env_vars(
            obj=self.sample_hyperparameters,
            group='mldock'
        )

        assert result == self.sample_hyperparameter_validation, (
            "Failed, Keys were not in MLDOCK format"
        )

    def test_collect_mldock_environment_variables(self):
        """test format key for environment vars"""

        result = collect_mldock_environment_variables(
            stage='dev',
            hyperparameters=self.sample_hyperparameters['hyperparameters'],
            environment=self.sample_environment
        )

        assert result == self.sample_collected_mldock_env_vars, (
            "Failed, Keys were not in MLDOCK format"
        )
