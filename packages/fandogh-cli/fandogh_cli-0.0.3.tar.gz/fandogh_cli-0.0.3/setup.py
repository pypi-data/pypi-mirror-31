from distutils.core import setup

import setuptools

setup(
    name='fandogh_cli',
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    version='0.0.3',
    description='Official CLI for Fandogh PaaS',
    author='Soroosh Sarabadani',
    install_requires=["click",
                      "requests",
                      "beautifultable",
                      "pyyaml"],
    author_email='soroosh.sarabadani@gmail.com',
    url='https://github.com/psycho-ir/fandogh-cli',
    keywords=['PaaS', 'Fandogh'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    entry_points='''
        [console_scripts]
        fandogh=fandogh_cli.fandogh:base
    ''',

)
