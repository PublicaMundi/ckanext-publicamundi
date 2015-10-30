from setuptools import setup, find_packages
import sys, os

version = '1.3dev'

setup(
    name='ckanext-publicamundi',
    version=version,
    description="A collection of CKAN plugins developed for PublicaMundi project",
    long_description="""\
    """,
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='ckan catalog open-data',
    author='Michail Alexakis',
    author_email='alexakis@imis.athena-innovation.gr',
    url='https://github.com/PublicaMundi/ckanext-publicamundi',
    license='GPLv3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.publicamundi'],
    include_package_data=True,
    paster_plugins=['pylons', 'ckan'],
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        # Note: Moved under requirements.txt
    ],
    entry_points=\
    """
        [ckan.plugins]

        publicamundi_dataset = ckanext.publicamundi.plugins:DatasetForm

        publicamundi_dataset_with_spatial = ckanext.publicamundi.plugins:SpatialDatasetForm
        
        publicamundi_package = ckanext.publicamundi.plugins:PackageController

        publicamundi_errorware = ckanext.publicamundi.plugins:ErrorHandler
        
        publicamundi_geodata_theme = ckanext.publicamundi.themes.geodata.plugin:GeodataThemePlugin

        publicamundi_vector = ckanext.publicamundi.storers.vector.plugin:VectorStorer

        publicamundi_raster = ckanext.publicamundi.storers.raster.plugin:RasterStorer
       
        publicamundi_analytics = ckanext.publicamundi.analytics.plugin:AnalyticsPlugin

        [paste.paster_command]
        
        publicamundi-setup = ckanext.publicamundi.commands:Setup

        publicamundi-cleanup = ckanext.publicamundi.commands:Cleanup
        
        publicamundi = ckanext.publicamundi.commands:Command
        
        #publicamundi-example1 = ckanext.publicamundi.commands:Example1

        [babel.extractors]
        
        publicamundi_extract_json = ckanext.publicamundi.lib.metadata.vocabularies.babel_extractors:extract_json
        
        [fanstatic.libraries]
        
        [ckan.celery_task]
        
        vector_tasks = ckanext.publicamundi.storers.vector.celery_import:task_imports
    
        raster_taks = ckanext.publicamundi.storers.raster.celery_import:task_imports
        
    """,
    # The following only stands as an example. The actual message_extractors should be defined into 
    # ckan's setup.py (from where message extraction is invoked).
    message_extractors = {
        'ckanext/publicamundi': [
            ('reference_data/inspire-vocabularies.json', 'publicamundi_extract_json', None),
            ('reference_data/language-codes.json', 'publicamundi_extract_json', None),
            ('**.py', 'python', None),
            ('**.html', 'ckan', None),
            #('multilingual/solr/*.txt', 'ignore', None),
            #('**.txt', 'genshi', {
            #    'template_class': 'genshi.template:TextTemplate'
            #}),
        ]
    }
)
