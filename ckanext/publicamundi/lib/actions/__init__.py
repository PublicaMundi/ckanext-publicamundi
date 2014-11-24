# Define some usefull exceptions 

class NameConflict(ValueError):
    '''Represent a name conflict which cannot be resoved automatically.
    '''
    pass

class InvalidParameter(ValueError):
    '''Represent an invalid parameter passed to an action.
    '''
    def __init__(self, msg, parameter_name=None):
        super(InvalidParameter, self).__init__(msg)
        self.parameter_name = parameter_name
   

# Import action modules

from ckanext.publicamundi.lib.actions import package
from ckanext.publicamundi.lib.actions import autocomplete

