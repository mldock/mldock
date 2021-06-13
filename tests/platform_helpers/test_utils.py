""" Test Utility methods used in platform helpers module"""
import json
import tempfile
from pathlib import Path
from mldock.platform_helpers import utils

class TestUtilsStorage:
    """ Collection of Tests for Utility methods used in platform helpers module"""

    @staticmethod
    def test_get_env_vars_success_on_filter():
        """
            Tests get_env_vars for successfully
            getting all env_vars on filter
        """
        env_vars = {
            "MYTESTVAR1": "2550",
            "_MYTESTVAR2": "a value",
            "MYTESTVAR3_": json.dumps(["a", "list", "example"]),
            "MYTESTVAR4": json.dumps({"key": "value"})
        }
        valid_vars = [{"key": key, 'value': value} for key,value in env_vars.items()]

        with utils.set_env(**env_vars):

            result = utils.get_env_vars(env_vars, ".*MYTESTVAR.*")

        assert result == valid_vars, (
            "Failed. get_env_vars did not produce the expected vars."
        )

    @staticmethod
    def test_delete_file_successful():
        """test delete file successfully removes file"""
        with tempfile.TemporaryDirectory() as tempdir:
            # create file
            file_path = Path(tempdir,'TEST_FILE.txt')
            file_path.touch()

            utils._delete_file(file_path)

            assert (Path(tempdir,'TEST_FILE.txt').is_file() == False), "Fail. Delete file was not successful"

    @staticmethod
    def test_mkdir_successful():
        """test make directory is successfully"""
        with tempfile.TemporaryDirectory() as tempdir:
            # create file
            file_path = Path(tempdir,'TESTPATH')
            
            utils._mkdir(dir_path=file_path)

            assert Path(tempdir,'TESTPATH').is_dir(), "Fail. Make directory was not successful"

    @staticmethod
    def test_list_nested_directories_successful():
        """test listing nested directories successfully"""
        with tempfile.TemporaryDirectory() as tempdir:
            # create file
            file_path = Path(tempdir, 'TESTPATH')
            
            utils._mkdir(dir_path=file_path)

            nested_files = [p.as_posix() for p in utils._iter_nested_dir(tempdir)]

            assert nested_files == [file_path.as_posix()], "Fail. Listing nested directories was not successful"

    @staticmethod
    def test_check_if_cloud_scheme():
        """tests method for checking that string is a s3 url"""
        url = 'gs://bucket/my/path/to/file.txt'

        assert utils._check_if_cloud_scheme(url, scheme='gs'), "Fail. check for gs url scheme was not successful"

    @staticmethod
    def test_strip_scheme():
        """tests method for checking that string is a s3 url"""
        url = 'gs://bucket/my/path/to/file.txt'
        validation = 'bucket/my/path/to/file.txt'

        assert utils.strip_scheme(url) == validation, "Fail. strip scheme from url was not successful"

    @staticmethod
    def test_parse_url_is_successful():
        """test method to parse url to bucket and filepath"""
        url = 'gs://bucket/my/path/to/file.txt'
        bucket, filepath = utils.parse_url(url, scheme='gs')

        assert bucket == 'bucket', "Fail. Parsing url for bucket was not successful"
        assert filepath == 'my/path/to/file.txt', "Fail. Parsing url for filepath was not successful"

    @staticmethod
    def test_zip_and_remove_original_folder_successful():

        with tempfile.TemporaryDirectory() as tempdir:
            # create file
            file_path = Path(tempdir, 'TEST_PATH')
            
            utils._mkdir(dir_path=file_path)
            Path(file_path, 'TEST_FILE.txt').touch()

            output_file = Path(file_path, 'zipped.zip')

            # create and zip folder as .zip
            utils.zip_folder(file_path, output_file, rm_original=True)

            output_file_list = [p.as_posix() for p in utils._iter_nested_dir(file_path)]

            assert output_file.is_file(), "Fail. Zip and remove original was not successful"
            assert len(output_file_list) == 1, "Fail. Zip and remove original was not successful"

    @staticmethod
    def test_zip_to_tarfile_and_rm_original_folder_successful():

        with tempfile.TemporaryDirectory() as tempdir:
            # create file
            file_path = Path(tempdir,'TESTPATH')
            
            utils._mkdir(dir_path=file_path)
            Path(file_path, 'TEST_FILE.txt').touch()

            output_file = Path(file_path, 'zipped.tar.gz')

            # create and zip folder as .tar.gz
            utils.zip_folder_as_tarfile(file_path, output_file, rm_original=True)

            output_file_list = [p.as_posix() for p in utils._iter_nested_dir(file_path)]

            assert output_file.is_file(), "Fail. Zip (tar) and remove original was not successful"
            assert len(output_file_list) == 1, "Fail. Zip (tar) and remove original was not successful"


    @staticmethod
    def test_unzip_and_remove_original_folder_successful():

        with tempfile.TemporaryDirectory() as tempdir:
            # create file
            file_path = Path(tempdir, 'TEST_PATH')
            
            utils._mkdir(dir_path=file_path)
            Path(file_path, 'TEST_FILE.txt').touch()

            output_file = Path(file_path, 'zipped.zip')

            # create and zip folder as .zip
            utils.zip_folder(file_path, output_file, rm_original=True)

            utils.unzip_file(output_file, file_path, rm_zipped=True)

            output_file_list = [p.name for p in utils._iter_nested_dir(file_path)]

            assert output_file_list == ['TEST_FILE.txt'], "Fail. Zip and remove original was not successful"

    @staticmethod
    def test_unzip_file_from_tarfile_and_rm_original_folder_successful():

        with tempfile.TemporaryDirectory() as tempdir:
            # create file
            file_path = Path(tempdir,'TESTPATH')
            
            utils._mkdir(dir_path=file_path)
            Path(file_path, 'TEST_FILE.txt').touch()

            output_file = Path(file_path, 'zipped.tar.gz')

            # create and zip folder as .tar.gz
            utils.zip_folder_as_tarfile(file_path, output_file, rm_original=True)

            utils.unzip_file_from_tarfile(output_file, file_path, rm_zipped=True)

            output_file_list = [p.name for p in utils._iter_nested_dir(file_path)]

            assert output_file_list == ['TEST_FILE.txt'], "Fail. Zip and remove original was not successful"
