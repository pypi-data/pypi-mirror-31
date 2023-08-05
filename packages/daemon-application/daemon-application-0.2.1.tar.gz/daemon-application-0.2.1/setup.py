import os
from io import open
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

requires = [
    "six",
    "psutil",
]

setup(
    name="daemon-application",
    version="0.2.1",
    description="Daemon application help functions.",
    long_description=long_description,
    url="https://github.com/appstore-zencore/daemon-application.git",
    author="zencore",
    author_email="dobetter@zencore.cn",
    license="MIT",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords=['daemon-application'],
    packages=find_packages("src"),
    package_dir={"": "src"},
    zip_safe=False,
    requires=requires,
    install_requires=requires,
)