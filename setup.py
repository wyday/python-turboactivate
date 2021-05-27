#!/usr/bin/env python

import setuptools
from distutils.core import setup

setup(name="turboactivate",
      version="4.4.4.1",
      description="Python integration for the LimeLM TurboActivate library. This lets you add hardware-locked licensing (a.k.a. node-locked licensing) to your Python app.",
      url="https://wyday.com/limelm/help/using-turboactivate-with-python/",
      download_url="https://github.com/wyday/python-turboactivate",
      author="Develer S.r.L",
      author_email="info@develer.com",
      maintainer="wyDay, LLC",
      maintainer_email="support@wyday.com",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Topic :: Software Development :: Libraries :: Python Modules',
		  'Programming Language :: Python',
		  'Programming Language :: Python :: 2',
		  'Programming Language :: Python :: 3',
      ],
      packages=["turboactivate"],
      long_description=open("README.md").read(),
      long_description_content_type="text/markdown"
)
