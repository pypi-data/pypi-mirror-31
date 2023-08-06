#!/usr/bin/env python
# -*- coding:utf-8 -*-


from setuptools import setup, find_packages

setup(
    name="chrhyme",
    version="0.1.1",
    author="Jiajie Yan",
    author_email="jiaeyan@gmail.com",
    description="find rhymes for Chinese words",
    long_description=open("README.md").read(),
    license="MIT",
    url="https://github.com/jiaeyan/Chinese-Rhyme",
    keywords=['chinese', 'rhymes', 'rhythm', 'rap', 'rapper', 'hip-pop', 'poem'],
    packages=find_packages(),
    install_requires=["pypinyin"],
    python_requires='>=3',
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ]
)