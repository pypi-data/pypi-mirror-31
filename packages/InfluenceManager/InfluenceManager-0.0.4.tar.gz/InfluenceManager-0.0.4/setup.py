"""
Backend module for retrieving top influencers from Twitter.
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="InfluenceManager",
    version="0.0.4",
    description="Backend module for retrieving top influencers from Twitter.",
    long_description=long_description,
    author="Ash Prince",
    author_email="i7629228@bournemouth.ac.uk",
    packages=find_packages(),
    include_package_data=True,
    scripts=["InfluenceManager/bin/topic_query"],
    install_requires=[]
)
