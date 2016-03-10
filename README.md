# gedit-pythonchecker

This library is a Gedit plugin which checks Python code syntax for active documents opened in Gedit.

Prerequisites
-------------

It is needed at least:

* Gedit 3.4+
* Python 3.2+
* python3-pep8
* python3-pylint
* gir1.2-gtksource-3.0

Please be sure that `python3` versions of `pep8` and `pylint` are called when using these commands in a terminal (and not the corresponding `python2` versions). This is currently necessary because these paths are still not configurable.

Installation
------------

Download the library and copy the folder `pythonchecker` and the file `pythonchecker.plugin` into the folder `~/.local/share/gedit/plugins`. In case it does not exist, you will have to create it first.

Once the plugin is correctly installed, it can be enabled through `Edit > Preferences > Plugins`. A new tab will be shown in the side panel of Gedit.

Reporting bugs
--------------

This library is currently in development and its state is still alpha. For
reporting bugs, feel free to open an issue at
http://github.com/molinav/gedit-pythonchecker/issues.
