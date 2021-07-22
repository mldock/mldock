"""
    AWS STORAGE HELPERS

    Provides a set of helpers to intereact with aws s3 storage api's for asset management tasks.
"""
import os
from pathlib import Path
import logging
import boto3

from mldock.platform_helpers.utils import \
    _mkdir, _iter_nested_dir, _check_if_cloud_scheme, \
        parse_url, zip_folder_as_tarfile, unzip_file_from_tarfile, \
            unzip_file

logger = logging.getLogger('mldock')

def download_file_from_bucket(bucket, blob, prefix, filename, target):
    """
        download file from s3 bucket

        args:
            bucket (str): s3 bucket name
            blob (S3Blob): s3 blob object
            prefix (str): prefix filepath in bucket
            filename (str): filename
            target (str): target directory on local
    """
    dst_filepath = os.path.join(target, os.path.basename(prefix))
    file_destination = os.path.join(dst_filepath, filename)

    logger.info("Download {} to local at {}".format(filename, file_destination))
    # make directory
    _mkdir(dst_filepath)
    # download
    bucket.download_file(blob.key, file_destination)

def download_folder(
    bucket_name: str,
    prefix: str,
    target: str
):
    """download folder from google cloud storage, ignoring folders.

    Args:
        bucket_name (str): [description]
        prefix (str): [description]
        target (str): [description]
    """
    logger.info("Starting Folder download from s3 storage")
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(bucket_name)

    for blob in bucket.objects.filter(Prefix = prefix):
        filename = Path(blob.key).name

        if len(filename) > 0:
            download_file_from_bucket(bucket, blob, prefix, filename, target)

def upload_file_to_bucket(bucket, path, storage_destination):
    """
        Upload file from local to bucket.

        args:
            bucket (S3bucket): s3 bucket object
            path (str): path to object in local
            storage_destination: path to object path in storage
    """
    logger.info("Upload {} to cloud at {}".format(path, storage_destination))
    bucket.upload_file(path.as_posix(), storage_destination)

def upload_folder(local_path: str, bucket_name: str, prefix: str):
    """Upload folder and contents to cloud storage

    Args:
        local_path (str): path to local directory
        bucket_name (str): bucket name to upload files to
        prefix (str): cloud filepath to write files to
    """
    logger.info("Starting Folder Upload to cloud storage")
    # get bucket
    s3_resource = boto3.resource("s3")
    bucket = s3_resource.Bucket(bucket_name)

    assert os.path.isdir(local_path), "'{}' is not a directory".format(local_path)

    for path in _iter_nested_dir(local_path):
        filepath = path.relative_to(local_path)
        storage_destination = os.path.join(prefix, filepath)
        if path.is_file():
            upload_file_to_bucket(bucket, path, storage_destination)

def download_input_assets(storage_dir_path: str, local_path: str, scheme: str):
    """download input asset folder from path, given that path is cloud storage path.

    Args:
        storage_dir_path (str): path to data in cloud storage
        local_path (str): where data should be stored (this comes from the environment).
        scheme (str, optional): scheme for cloud storage url. Defaults to 'gs'.
    """
    is_cloud_storage = _check_if_cloud_scheme(url=storage_dir_path, scheme=scheme)

    if is_cloud_storage:
        # download data if cloud storage path
        bucket, prefix = parse_url(url=storage_dir_path, scheme=scheme)
        download_folder(bucket_name=bucket, prefix=prefix, target=local_path)

        for file_path in Path(local_path).glob('*/*'):
            if file_path.suffix == '.zip':
                unzip_file(filename=file_path, output_dir=file_path.parent, rm_zipped=True)
            elif file_path.suffix == '.gz':
                unzip_file_from_tarfile(
                    filename=file_path,
                    output_dir=file_path.parent,
                    rm_zipped=True
                )
    else:
        Exception("No Cloud storage url was found. Must have gs:// schema")

def package_and_upload_model_dir(local_path: str, storage_dir_path: str, scheme: str):
    """
        Packages model/ dir as .tar.gz and uploads to cloud storage, given that storage_dir_path
        is cloud storage url path.

        Args:
            local_path (str): path to model directory
            storage_dir_path (str): cloud storage path destination
            scheme (str, optional): cloud storage url scheme. Defaults to 'gs'.
    """
    is_cloud_storage = _check_if_cloud_scheme(url=storage_dir_path, scheme=scheme)
    if is_cloud_storage:
        zip_folder_as_tarfile(
            dir_path=local_path,
            output_file=os.path.join(local_path, 'model.tar.gz'),
            rm_original=True
        )
        bucket, prefix = parse_url(url=storage_dir_path, scheme=scheme)
        upload_folder(local_path=local_path, bucket_name=bucket, prefix=prefix)
    else:
        Exception("No Cloud storage url was found. Must have gs:// schema")

def package_and_upload_output_data_dir(local_path: str, storage_dir_path: str, scheme: str):
    """
        Packages output/ dir as .tar.gz and uploads to cloud storage, given that storage_dir_path
        is cloud storage url path.

        Args:
            local_path (str): path to model directory
            storage_dir_path (str): cloud storage path destination
            scheme (str, optional): cloud storage url scheme. Defaults to 'gs'.
    """
    is_cloud_storage = _check_if_cloud_scheme(url=storage_dir_path, scheme=scheme)

    if is_cloud_storage:
        bucket, prefix = parse_url(url=storage_dir_path, scheme=scheme)
        upload_folder(local_path=local_path, bucket_name=bucket, prefix=prefix)
    else:
        Exception("No Cloud storage url was found. Must have gs:// schema")
