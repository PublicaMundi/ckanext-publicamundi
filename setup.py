from setuptools import setup, find_packages
import sys, os

version = '0.8'

setup(
	name='ckanext-helloworld',
	version=version,
	description="hello world",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='malex',
	author_email='malex@example.net',
	url='',
	license='',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.helloworld'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
        "jsonpickle",
	],
	entry_points=\
	"""
        [ckan.plugins]

        helloworld_dataset = ckanext.helloworld.plugins:DatasetForm

        [paste.paster_command]

        helloworld-greet = ckanext.helloworld.commands:Greet

        [fanstatic.libraries]

	""",
)
