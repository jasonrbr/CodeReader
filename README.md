# CodeReader

_Madeline Andrew, Alexandra Brown, Jason Brown, Benny Ng_

This Sublime Text 3 extension works by giving context-rich readings and organization of code. It breaks code into different hierarchies (functions, classes, etc) and offers the user a concise and easy-to-navigate user interface for understanding these scopes.

Requirements: Python 3, Sublime Text 3

To install, pull this folder along the path:

Windows: c:\users\<username>\AppData\Roaming\Sublime Text 3\Packages

Mac: /Users/<username>/Library/Application Support/Sublime Text 3/Packages/

For the alpha release, we have implemented the main menu for navigation. To run this plugin, open _test_alpha.cpp_ and run in the sublime console _view.run_command('code_reader')_. This menu will present available functions and classes to navigate to and read. It supports "going up" a hierarchy level as well. Currently, these functions will be printed to the console. It will be simple in the beta release to convert this text to speech.