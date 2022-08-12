from setuptools import setup, find_packages
from aminoacid import __version__, __author__

with open("requirements.txt", "r") as file:
    INSTALL_REQUIRES = file.readlines()

with open("README.md") as readme:
    setup(
        name="aminoacid",
        version=__version__,
        description="Async library for creating Bots for amino",
        long_description=readme.read(),
        long_description_content_type="text/markdown",
        license="MIT License",
        author=__author__,
        author_email="okok7711@etstun.de",
        url="https://github.com/okok7711/AminoAcid",
        classifiers=[
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
        ],
        keywords="amino, internet, bot, async",
        install_requires=INSTALL_REQUIRES,
        packages=find_packages(),
    )
