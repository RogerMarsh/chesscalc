# setup.py
# Copyright 2012 Roger Marsh
# Licence: See LICENCE (BSD licence)
"""chesscalc setup file."""

from setuptools import setup

if __name__ == "__main__":

    long_description = open("README").read()

    setup(
        name="chesscalc",
        version="1.2.2",
        description="Calculate player performances in chess games",
        author="Roger Marsh",
        author_email="roger.marsh@solentware.co.uk",
        url="http://www.solentware.co.uk",
        packages=[
            "chesscalc",
            "chesscalc.core",
            "chesscalc.gui",
            "chesscalc.help",
        ],
        package_data={
            "chesscalc.help": ["*.txt"],
        },
        long_description=long_description,
        license="BSD",
        classifiers=[
            "License :: OSI Approved :: BSD License",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Operating System :: OS Independent",
            "Topic :: Games/Entertainment :: Board Games",
            "Intended Audience :: End Users/Desktop",
            "Intended Audience :: Developers",
            "Development Status :: 3 - Alpha",
        ],
        install_requires=["solentware-misc==1.3.1"],
        dependency_links=[
            "http://solentware.co.uk/files/solentware-misc-1.3.1.tar.gz",
        ],
    )
