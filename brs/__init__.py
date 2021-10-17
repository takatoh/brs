# brs
__version__ = '0.8.1'


CONFIG_FILE_NAME = '.brsconfig.yml'


class NoTitleException(Exception):
    def __str__(self):
        return 'No title found.'

class ConfigLocationError(Exception):
    def __str__(self):
        return 'No config file found or settled.'
