from pathlib import Path
import glob
import setuptools
from mldock.__version__ import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

def get_package_data(relative_path, relative_to):

    paths = Path(relative_to,relative_path).glob('**/*')
    data_files = [p.relative_to(relative_to).as_posix() for p in paths]

    return data_files

setuptools.setup(
    name="mldock",
    version=__version__,
    author="SheldonGrant",
    author_email="sheldz.shakes.williams@gmail.com",
    description="A docker tool that helps put machine learning in places that empower ml developers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mldock/mldock",
    packages=setuptools.find_packages(where='.'),
    package_data={
        'mldock': get_package_data(
            relative_path='templates',
            relative_to='mldock'
        )
    },
    setup_requires=['setuptools>=39.1.0'],
    install_requires=['future', 'environs', 'PyGithub'],
    extras_require={
        'gcp': [
            'google-cloud-storage',
            'google-api-python-client',
            'gcsfs',
            'pyarrow'
        ],
        'aws': [
            'boto3',
            's3fs',
            'pyarrow'
        ],
        'cli': [
            'click',
            'clickclick',
            'docker',
            'future',
            'requests',
            'boto3',
            'google-auth',
            'appdirs',
            'halo',
            'PyYAML',
            'pygrok',
            'gcsfs',
            's3fs',
            'pyarrow',
            'wheel'
        ],
        'sagemaker': ['sagemaker-training'],
        'inference': ['pandas', 'numpy', 'protobuf>=3.1', 'Pillow'],
        'testing': ['responses', 'dataclasses'],
        'pyarrow-gcs': [
            'gcsfs',
            'pyarrow',
        ],
        'pyarrow-s3': [
            's3fs',
            'pyarrow',
        ]
    },
    entry_points="""
        [console_scripts]
        mldock=mldock.__main__:cli
    """,
    keywords=["docker", "machine learning", "ml", "ml services", "MLaaS"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6"
    ],
    python_requires='>=3.6',
)
