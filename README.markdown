<!-- -*- mode: markdown -*- -->
Coffee Notes
------------

### About

![](https://github.com/dmych/cn/raw/master/icon.png)

**Coffee Notes** is crossplatform note-taking application inspired by *Notational Velocity*.

Initial release was sketched by me while I was drinking coffee in the coffee house. :)

### User Guide

#### Requirements

This app is written in **Python 2.6** and uses **PyQt4**.

#### Installation

1. Go to [Downloads](https://github.com/dmych/cn/downloads) to download **deb**-package; then as usual, `sudo dpkg --install <deb-name>`; *Coffee Notes* should appear in *Accesories* section of the main menu.
2. Click [Zip](https://github.com/dmych/cn/zipball/master) button to download source code as zip-archive; unpack it to any directory and launch `cn.py`.

#### Using Coffee Notes

Run **Coffee Notes** and start typing your note — it will be saved automatically (first line become the note's title).

Press `Ctrl+L` and type anything in the search bar to find notes.

No need to click "Save" button! Everything you type will be saved immediately (actually, autosave goes off every 5 seconds by default, it can be changed — see `Autosave` parameter in config file below).

#### Shortcuts

* `Ctrl+N` — create new (empty) note
* `Ctrl+L` — switch to search bar/note text
* `Esc` — clear search/title bar
* `Ctrl+O` — toggle orientation to vertical/horizontal
* `Ctrl+D` — delete current note (if any)
* `Tab` — jump through search/title bar, notes list and text area
* `Ctrl+Q` — quit

#### Configuration File

Config file should be located in your home directory: `~/.cn.conf`. Here is a sample file:

    WorkDir=~/Dropbox/path/to/your/notes
    EditFont=Georgia, 14
    ListFont=Ubuntu, 12
    Autosave=5
    
* `WorkDir` reffers to the directory where your notes are stored (`~/Coffee Notes` by default)
* `EditFont` and `ListFont` set the font family and size for the note editor and notes list respectively
* `Autosave` sets autosave interval in seconds (must be integer, 5 by default).

### Syncing with Dropbox

*Coffee Notes* keeps all notes as a text files in a separate directory (`~/Coffee Notes` by default), you can just move this directory with its contents to your Dropbox directory — create `~/cn.conf` file and put there the following line:

    WorkDir=~/Dropbox/path/to/your/notes

Insead, you can create symlink: `ln -s ~/Dropbox/path/to/your/notes ~/Coffee\ Notes`

### Syncing with Simplenote

Planned in the nearest future releases. See Issue #9.

### Versioning

Major releases of *Coffee Notes* have names: Espresso, Americano, Cappiccino etc. Each version of the named major release has version in format Year.Month (such as 11.10) with optional letter ("a" for the "alpha" release, or "b" for "beta" release).
