# CodeReader

_Madeline Andrew, Alexandra Brown, Jason Brown, Benny Ng_

_EECS 481 - Software Engineering_

This Sublime Text 3 extension works by giving context-rich readings and organization of code. It breaks code into different hierarchies (functions, classes, etc) and offers the user a concise and easy-to-navigate user interface for understanding these scopes. It does this by linking to a python text to speech library to read code audibly to the user.

**Requirements**: Python 3, Sublime Text 3

**To install**, pull this folder along the path:

Windows: c:\users\<username>\AppData\Roaming\Sublime Text 3\Packages\

Mac: /Users/{username}/Library/Application Support/Sublime Text 3/Packages/

For the beta release, we have implemented a more comprehensive reading and navigation of functions/classes. We have also fully integrated our audio capabilities and parsing of classes and functions. Additionally, we have added a help menu along with key bindings to start the plugin. To run this plugin, open a _.cpp_ file and use the key binding _control+shift+c+r_ on Windows or _command+shift+c+r_ on Mac. This menu will present available functions and classes to navigate to and read in the global namespace. Select any child option in the menu to see more scopes. It supports "going up" a hierarchy level as well.

See developer_notes.txt for a list of C++ constructs this plugin does not support.
