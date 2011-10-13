Coffee Notes
------------

### About

![](https://github.com/dmych/cn/raw/master/icon.png) Mac users have *Notational Velocity*, Linux users have nothing. **Coffee Notes** is crossplatform application inspired by *Notational Velocity*.

Initial release was sketched by me while I was drinking coffee in the coffee house.

### Requirements

This app is written in **Python 2.6** and uses **PyQt4**.

### User Guide

Start typing in the search/title bar to find a note or set a new note's title, then hit `Enter` to open/create note.

Everything you type will be saved immediately. No need to click "Save" button.

Shortcuts:

* `Ctrl+L` — switch to search/title bar
* `Esc` — clear search/title bar
* `Ctrl+O` — toggle orientation to vertical/horizontal
* `Ctrl+Delete` — delete current note (if any)
* `Tab` — jump through search/title bar, notes list and text area
* `Ctrl+Q` — quit

### Syncing with Dropbox

*Coffee Notes* keeps all notes as a text files in a separate directory (`~/Coffee Notes` by default), you can just move this directory with its contents to your Dropbox directory — create `~/cn.conf` file and put there the following line:

    WorkDir=~/Dropbox/path/to/your/notes

Insead, you can create symlink: `ln -s ~/Dropbox/path/to/your/notes ~/Coffee\ Notes`
