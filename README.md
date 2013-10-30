Argument Noun
===========

Overview
--------

*Argument Noun* is a [Sublime Text 3](http://www.sublimetext.com/) plugin that extends the Vintage mode with a new arguments noun (text object): 'a'. It is is similar to the [argtextobj](http://www.vim.org/scripts/script.php?script_id=2699) plugin for Vim by Takahiro Suzuki.

Example: let's say you are editing `foo(a, b*(c+d))` and the caret is somewhere inside the second argument. Triggering the __c__hange-__i__nner-__a__rgument operation by typing `cia` then gives you `foo(a, )` and you can insert some text to replace the old argument.

[Read more about verbs, nouns and modifiers](http://yanpritzker.com/2011/12/16/learn-to-speak-vim-verbs-nouns-and-modifiers/)

Usage
-------

* _delete_ an argument with `daa`
* _change_ inner argument with `cia`
* _select_ inner argument with `via`
* _yank_ inner argument with `yia`

Installation
------------

* via [PackageControl](https://sublime.wbond.net/)

or

* clone to your Sublime Text 3 `Packages` folder located at
    * Windows: %APPDATA%\Sublime Text 3
    * OS X: ~/Library/Application Support/Sublime Text 3
    * Linux: ~/.config/sublime-text-3

Notes
----------

The plugin is quite syntax agnostic. It however makes the assumption that an argument list is wrapped in parenthesis, is preceded by a function name identifier, and that arguments are comma separated.

If two identifiers are separated by only a newline and white space it is assumed that a right parenthesis after the first identifier is missing, i.e.

    myfunction(a, b, c
    x = 5

is handled as if `c` had been followed by `)`. This ensures that the argument region does not get too large in case of incorrect syntax.

Only commas at the correct level of nesting are treated as argument separators so eg. usage of Python tuples shouldn't pose any problem.

Limitations
----------

Method calls without parenthesis (like in Ruby) are not supported at this time.

Comments intermingled with arguments are not supported at this time.

License
-----------

MIT License

Contributors
-----------

Created by Nils Liberg
