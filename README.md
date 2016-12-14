# CodeReader

_Madeline Andrew, Alexandra Brown, Jason Brown, Benny Ng_

_EECS 481 - Software Engineering_

This Sublime Text 3 extension works by giving context-rich readings and organization of code. It breaks code into different hierarchies (functions, classes, etc) and offers the user a concise and easy-to-navigate user interface for understanding these scopes. It does this by linking to a python text to speech library to read code audibly to the user.

**Requirements**: Python 3, Sublime Text 3

**To install**, pull this folder along the path:

Windows: c:\users\<username>\AppData\Roaming\Sublime Text 3\Packages\

Mac: /Users/{username}/Library/Application Support/Sublime Text 3/Packages/

The current state of this plugin is that it reads classes, functions, and included libraries. It offers customizable audio speeds and toggable readings of line numbers or comments. See the help menu for more details about these key bindings. This plugin will parse these scopes and present them in a sublime menu to be read audibly. Use the arrow keys or the mouse to navigate through this menu.

See developer_notes.txt for a list of C++ constructs this plugin does not support.
