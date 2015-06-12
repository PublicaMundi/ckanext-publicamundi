import sys
import os.path
import logging
import optparse
from optparse import make_option 
import paste.script

from ckan.lib.cli import CkanCommand

def parser_error(msg):
    '''Monkey-patch for optparse parser's error() method.
    This is used whenever we want to prevent the default exit() behaviour.
    '''
    raise ValueError(msg)

class CommandDispatcher(CkanCommand):
    '''A command dispatcher for various publicamundi-related subcommands'''

    __usage = '''paster [PASTER-OPTS] publicamundi --config FILE [--setup-app] %(name)s [%(name)s-OPTS] ARGS'''

    __specs = {}

    @staticmethod
    def get_subcommand_spec(name):
        return CommandDispatcher.__specs.get(name)   
    
    @staticmethod
    def get_subcommand_specs():
        return CommandDispatcher.__specs.items()   
    
    @staticmethod
    def get_subcommand_usage(name):
        return CommandDispatcher.__usage %(dict(name=name))

    @staticmethod
    def subcommand(name, options=[]):
        '''A parameterized decorator to mark methods of derived classes as subcommands'''
        def decorate(method):
            CommandDispatcher.__specs.update({
                name: {
                    'method': method,
                    'options': options,
                },
            })
            return method
        return decorate
    
    def __init__(self, name):
        CkanCommand.__init__(self, name)
        parser = self.parser
        
        if 'CKAN_CONFIG' in os.environ:
            parser.remove_option('--config')
            parser.add_option('--config', 
                type=str, dest='config', default=os.environ['CKAN_CONFIG'])

        parser.add_option('--setup-app', 
            action='store_true', dest='setup_app', default=False)
        
        parser.disable_interspersed_args()        
        return

    def command(self):        
        '''Load environment, parse args and dispatch to the proper subcommand
        '''

        if self.options.config:
            self._load_config()
        
        if self.options.setup_app:
            self._setup_app()

        self.logger = logging.getLogger('ckanext.publicamundi')
        self.logger.setLevel(logging.INFO)
        
        self.logger.debug('Remaining args are ' + repr(self.args))
        self.logger.debug('Options are ' + repr(self.options))

        subcommand = self.args.pop(0) if self.args else '?'

        if subcommand == 'help':
            print self.__doc__
            return

        spec = self.get_subcommand_spec(subcommand)
        if spec:
            method = spec['method']
            parser = self.standard_parser()
            parser.set_usage(self.get_subcommand_usage(subcommand))
            parser.error = parser_error
            parser.add_options(option_list=spec.get('options'))
            try:
                opts, args = parser.parse_args(args=self.args)
            except Exception as ex:
                self.logger.error('Bad options for subcommand %s: %s', subcommand, str(ex))
                print 
                print method.__doc__
                print
                parser.print_help()
                return
            else:
                self.logger.debug('Trying to invoke "%s" with: opts=%r, args=%s' %(
                    subcommand, opts, args))
                return method(self, opts, *args)
        else:
            if subcommand != '?':
                self.logger.error('Got an unknown subcommand: %s' %(subcommand))
            print 'The available publicamundi commands are:\n'
            for k, spec in self.get_subcommand_specs():
                method = spec['method']    
                print ' * %s: %s\n' %(k, method.__doc__.split("\n")[0])
            return
    
