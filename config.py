import json
import os
import sublime
import sublime_plugin


class Config:
    '''Config class to serve as a container and obejct for CodeReader
    configurations
    Formatted as a json file, but loaded as a dictionary in memory'''
    is_initialized = False
    DEFAULT_CONFIG = {
        'read_comments': True,
        'read_line_numbers': True,

    }
    config = {}
    package_dir = 'CodeReader'
    config_fn = os.path.join(sublime.packages_path(),
                             package_dir, '.cr_config')

    @staticmethod
    def init(fn=None, config={}):
        '''
        Will initialize the Config object with a given config, if
        given one. Otherwise it will default to just the default
        configuration file.
        Will try to load the defaultly named config file if it exists.
        Otherwise, it will merely have the default configurations.
        '''

        # load the file from memory or default

        Config.is_initialized = True
        if not fn:
            Config.config = Config.DEFAULT_CONFIG
            Config._save_config()
        else:

            Config.config_fn = os.path.join(sublime.packages_path(),
                                            Config.package_dir, fn)
            Config._load_config()
            Config.config_fn = fn

        # load param config file into our config
        for k in config:
            Config.config[k] = config[k]

    @staticmethod
    def get(param):
        '''
        Returns the value set for the given parameter in the config file.
        Will return None if the value is unset.
        '''
        if param in Config.config:
            return Config.config[param]
        else:
            return None

    @staticmethod
    def set(param, value):
        Config.config[param] = value
        Config._save_config()

    # loads config file into memory
    #   @param: fn: filename of the config file
    @staticmethod
    def _load_config():
        print('loading from:', Config.config_fn)
        try:
            f = open(Config.config_fn, 'r')
            Config.config = json.loads(f.read())
        except:
            print("Error reading config file.")

    #  saves config file in memory to file
    #   @param: fn: filename of the config file
    @staticmethod
    def _save_config():
        print('saving to:', Config.config_fn)
        try:
            f = open(Config.config_fn, 'w')
            f.write(json.dumps(Config.config))
        except:
            print("Error saving to config file. Write failed.")

    @staticmethod
    def toggle(param):
        val = not Config.get(param)
        Config.set(param, val)

    @staticmethod
    def _tostring():
        return str(Config.config)


class ToggleLineNumbersCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        Config.toggle('read_line_numbers')


class ToggleCommentsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        Config.toggle('read_comments')


Config.init()
