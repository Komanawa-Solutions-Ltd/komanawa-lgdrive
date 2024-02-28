"""
created matt_dumont 
on: 24/03/22
"""
import os
from setuptools import setup, find_packages, find_namespace_packages

BUILD_ID = os.environ.get("BUILD_BUILDID", "0")

setup(
    name="komanawa-lgdrive",
    version="v1.1.0",
    # Author details
    author="Matt Dumont",
    author_email="hansonmcoombs@gmail.com",
    packages=find_namespace_packages(where='src/'),
    package_dir={"": "src"},
    package_data={'komanawa/lgdrive':['*.png']},
    setup_requires=[],
    tests_require=[],
    extras_require={},
    install_requires=[
        "fire",
    ],
    python_requires=">=3.9"
)
