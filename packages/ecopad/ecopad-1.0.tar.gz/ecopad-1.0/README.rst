ecopad
======

A tool for padding text to be pasted into text boxes in the game Eco,
working around a client bug on linux, that doubles key presses.

Packages needed before installing
---------------------------------

-  python3-tkinter

Installation
------------

``pip3 install --user ecopad``

Usage
-----

Launch the app with the command ``ecopad``. Alternately, one may add the
option ``-L`` for 4K monitors.

Once the app is open, entering text into the entry field and pressing
return, or clicking the button, will copy the text to clipboard, and pad
it with whitespace if the length is odd numbered. Once pasted inside the
game, one simply deletes the doubled phrase, and submit the text.
