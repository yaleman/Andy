# About this codebase 

Andy is the little Bot that Could.

I guess the aim is to make my own little intelligent agent, pulling in information from everywhere I can and generally making my day easier. I'll try and make it as modular as possible so code reuse is possible wherever I can :)

# Adding a new plugin

* Create a new folder in toolbox/plugins
* Create an *\__init__.py* file  inside it
* In the file:
 * Import toolbox
 * Make a class in it that imports *toolbox.base_plugin* called Plugin
 * Set the plugin name through *self.pluginname*
 * Set the data save file in *config.filenames*, key should be *self.pluginname*
	
You should be able to call the plugin in *Andy.interact()* by typing *pluginname [action]*

## Default parts of plugins

* *self._data* - data storage that will be automatically loaded/saved on shutdown. If you want to change this, overload self._load and self._save before you do anything.
* *self._save* and *self._load* - save/load functionality for pickling *self._data*
* *self._help* - returns a list of non-private functions, will be expanding to use docstrings Some Day Soon. :)
* *self._handle_text* - parses the default data from *Andy.interact()* and runs public functions. *[pluginname] [publicfuncname]* will run said function.

# File Caching Notes
* If a file has an expiry of -1, it'll be cached forever
