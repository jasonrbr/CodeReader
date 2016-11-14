

class Config:
    """
    Config class to serve as a container and obejct for CodeReader 
        configurations
    Formatted as a json file, but loaded as a dictioanry in memory
    """
    DEFAULT_CONFIG = {
        'read_comments': False,
        'read_line_numbers': False,

    }

    DEFAULT_CONFIG_FN = '.cr_config'
    config_fn = DEFAULT_CONFIG_FN

    def __init__(self, fn=None, config={}):
        """
        Will initialize the Config object with a given config, if given
        one. Otherwise it will default to just the default
        configuration file.
        Will try to load the defaultly named config file if it exists.
        Otherwise, it will merely have the default configurations.
        """

        if not fn:
            self.config = self.DEFAULT_CONFIG
        else:

            fn = os.path.join(os.path.dirname(__file__), fn)
            self._load_config(fn)
            self.config_fn = fn

        for k in config:
            self.config[k] = config[k]

    def get(self):
        """
        Returns the entire config file
        """
        return self.config

    def get(self, param):
        """
        Returns the value set for the given parameter in the config file.
        Will return None if the value is unset.
        """
        if param in self.config:
            return self.config[param]
        else:
            return None

    def set(self, param, value):
        """
        Just sets the value for the parameter to the value, regardless
        of whether or not it currently exists
        Returns true if the action changes a previously set value
        """
        result = param in self.config
        self.config[param] = value
        self._save_config()
        return result

    def _load_config(self):
        """
        loads config file into memory
        parameters:
            fn - filename of the config file
        """

        print('loading:', self.fn)
        try:
            f = open(self.config_fn, 'r')
            s = f.read()
            # print(s)
            self.config = json.loads(f.read())
        except:
            print("Error reading config file.")

    def _save_config(self):
        """
        saves config file in memory to file
        parameters:
            fn - filename of the config file
        """
        print('saving to:', self.config_fn)
        try:
            f = open(self.config_fn, 'w')
            f.write(json.dumps(self.config))
        except:
            print("Error saving to config file. Write failed.")

    def __str__(self):
        return str(self.config)
