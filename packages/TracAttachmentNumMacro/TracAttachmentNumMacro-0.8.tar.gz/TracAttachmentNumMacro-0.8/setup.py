#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

__url__ = ur"$URL: https://trac-hacks.org/svn/attachmentnummacro/0.11/setup.py $"[
    6:-2]
__author__ = ur"$Author: rjollos $"[9:-2]
__revision__ = int("0" + ur"$Rev: 17134 $"[6:-2])
__date__ = ur"$Date: 2018-04-16 12:39:49 -0700 (Mon, 16 Apr 2018) $"[7:-2]


setup(
    name='TracAttachmentNumMacro',
    version='0.8',
    packages=['tracattachmentnum'],
    author='Martin Scharrer',
    author_email='martin@scharrer-online.de',
    description="Trac Macro to link to local attachments by number.",
    url='https://www.trac-hacks.org/wiki/AttachmentNumMacro',
    license='GPLv3',
    zip_safe=False,
    keywords='trac attachment number macro',
    install_requires=['Trac'],
    classifiers=['Framework :: Trac'],
    entry_points={'trac.plugins': [
        'tracattachmentnum.attachmentnum = tracattachmentnum.attachmentnum']}
)
