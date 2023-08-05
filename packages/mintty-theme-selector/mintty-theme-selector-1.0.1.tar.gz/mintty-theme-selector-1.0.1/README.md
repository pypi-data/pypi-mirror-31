Mintty Theme Selector
===

Python script to change between `mintty` themes from the command line

* [Save your themes][1] &mdash; `~/.mintty/themes`
* Install the script &mdash; `pip install mintty-theme-selector`
* List themes &mdash; `mts`
* Select a theme &mdash; `mts my-theme`

*Important*: `my-theme` is a regex which will be matched against theme filenames without extension, so `mts my-theme$` and similar works.

[1]: https://github.com/mintty/mintty/wiki/Tips
