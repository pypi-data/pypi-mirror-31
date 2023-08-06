#!/usr/bin/env python

# Project skeleton maintained at https://github.com/jaraco/skeleton

import io

import setuptools

with io.open('README.rst', encoding='utf-8') as readme:
	long_description = readme.read()

name = 'hgtools'
description = (
	'Classes and setuptools plugin for Mercurial and Git repositories')
nspkg_technique = 'native'
"""
Does this package use "native" namespace packages or
pkg_resources "managed" namespace packages?
"""

params = dict(
	name=name,
	use_scm_version=True,
	author="Jason R. Coombs",
	author_email="jaraco@jaraco.com",
	description=description or name,
	long_description=long_description,
	url="https://github.com/jaraco/" + name,
	packages=setuptools.find_packages(),
	include_package_data=True,
	namespace_packages=(
		name.split('.')[:-1] if nspkg_technique == 'managed'
		else []
	),
	python_requires='>=2.7',
	install_requires=[
		'jaraco.classes',
		'more_itertools',
		'packaging',
	],
	extras_require={
		'testing': [
			# upstream
			'pytest>=3.5',
			'pytest-sugar>=0.9.1',
			'collective.checkdocs',
			'pytest-flake8',

			# local
			'backports.unittest_mock',
			'pygments',
		],
		'docs': [
			# upstream
			'sphinx',
			'jaraco.packaging>=3.2',
			'rst.linker>=1.9',

			# local
		],
	},
	setup_requires=[
		'setuptools_scm>=1.15.0',
	],
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3",
		"Operating System :: OS Independent",
		"Topic :: Software Development :: Version Control",
		"Framework :: Setuptools Plugin",
	],
	entry_points={
		"setuptools.file_finders": [
			"hg = hgtools.plugins:file_finder"
		],
		"distutils.setup_keywords": [
			"use_hg_version = hgtools.plugins:version_calc",
			"use_vcs_version = hgtools.plugins:version_calc",
		],
	},
)
if __name__ == '__main__':
	setuptools.setup(**params)
