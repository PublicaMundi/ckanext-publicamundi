import paste.fixture
import pylons.test

import ckan.model as model
import ckan.tests as tests
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

class Test(object):

    @classmethod
    def setup_class(cls):
        '''Nose runs this method once to setup our test class.'''

        # Make the Paste TestApp that we'll use to simulate HTTP requests to CKAN.
        cls.app = paste.fixture.TestApp(pylons.test.pylonsapp)

        # Test code should use CKAN's plugins.load() to load plugins to be tested.
        plugins.load('publicamundi_dataset')

    def setup(self):
        '''Nose runs this method before each test method in our test class.'''
        pass

    def teardown(self):
        '''Nose runs this method after each test method in our test class.'''
        pass

    @classmethod
    def teardown_class(cls):
        '''Nose runs this method once after all the test methods in our class
        have been run.

        '''
        # We have to unload the plugin we loaded, so it doesn't affect any
        # tests that run after ours.
        plugins.unload('publicamundi_dataset')

    def test_1(self):
        pass
