"""

    - create: start a ngrok development server
    - upload: package and upload via secure copy to ngrok dev server.
    - train: run "upload", then execute train
    - deploy: run "upload", then execute deploy
"""
import paramiko
from pathlib import Path
from hashlib import md5
import zipfile

from mldock.platform_helpers.utils import iter_nested_dir, delete_file

def zip_folder(dir_path: str, output_file: str, rm_original: bool = True, include: list = None):
    """zip in directory and optionally throw away unzipped"""

    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipf:

        include = [Path(p) for p in include]
        for file in iter_nested_dir(dir_path):
            # every file starts with (yes, include)
            should_include = True

            if isinstance(include, list) and len(include) > 0:

                should_include = (file in include)

            if file.name != Path(output_file).name and file.is_file() and should_include:

                zipf.write(file)

                if rm_original:
                    delete_file(file)


def generate_hash_of_file(file_path):

    chunk_size = 8192

    h = md5()

    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if len(chunk):
                h.update(chunk)
            else:
                break

    return h.hexdigest()

def get_list_of_files(base_dir, include: list = None):
    """glob search directory for file paths"""
    if isinstance(include, list) and len(include) > 0:
        all_files = []
        for reg in include:
            tmp_base = Path(base_dir, reg)
            tmp = list(iter_nested_dir(tmp_base))
            all_files.extend(tmp)
    else:
        all_files = list(iter_nested_dir(base_dir))
    return all_files

def secure_copy_over_remote_ssh(local_filepath, remote_filepath, host, port, private_key_file):
    """use paramiko to execute create virtualenv, pip install & mldock local commands"""

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, key_filename=private_key_file)

    ftp_client=ssh.open_sftp()
    ftp_client.put(local_filepath, remote_filepath)
    ftp_client.close()

def execute_command_over_remote_ssh(command, host, port, private_key_file, requirements: list = None):
    """use paramiko to execute create virtualenv, pip install & mldock local commands"""

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, key_filename=private_key_file)

    stdin, stdout, stderr = ssh.exec_command(command)
    lines = stdout.readlines()
    print(lines)

def upload():
    """package and upload via secure copy to ngrok dev server."""

    input_file_dir = "./iris_classifier_py38_cpu"
    output_file_dir = "sandbox/check_zip_contents"
    compressed_file = Path(output_file_dir, "mldock.zip")

    # check if file exists
    old_hash = None
    if compressed_file.is_file():
        # get previous zip md5 code
        old_hash = generate_hash_of_file(compressed_file)

    # re-zip files (mldock.yaml, src)
    all_files = get_list_of_files(input_file_dir, include=["mldock.json", "mldock.yaml", "src/"])

    zip_folder(
        dir_path=input_file_dir,
        output_file=compressed_file,
        rm_original=False,
        include=all_files
    )
    # generate an md5 code
    new_hash = generate_hash_of_file(compressed_file)
    # if md5 is changed, run secure copy
    if new_hash == old_hash:
        print("hash is unchanged")
    else:
        print("uploading")
        secure_copy_over_remote_ssh(
            local_filepath=compressed_file,
            remote_filepath=Path(compressed_file).name,
            host = "X.tcp.ngrok.io",
            port = XXXXX,
            private_key_file = "/home/ubuntu_sw/.ssh/private_key_name"
        )
        print("unzip")
        execute_command_over_remote_ssh(
            command=f"unzip {Path(compressed_file).name}",
            host = "X.tcp.ngrok.io",
            port = XXXXX,
            private_key_file = "/home/ubuntu_sw/.ssh/private_key_name",
            requirements=None
        )
