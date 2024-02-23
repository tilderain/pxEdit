# pxEdit
## A collaborative editor for Studio Pixel games

<img src="https://github.com/tilderain/pxEdit/blob/kero/preview.png">
<img src="https://github.com/tilderain/pxEdit/blob/kero/preview2.png">

Experimental collaborative editor with high hopes. It attempts to emulate the style of Pixel's private editor, pxStage. The main draw is the ability to edit levels with other people.

It's basically a prototype that got out of control, so it's desperately in need of a rewrite, probably in Cython, C, or Rust.

## Usage
Download the packaged build from the releases page.

Or get sdl2, run python3 gxEdit.py. Requires "Kero Blaster" folder to be in the same folder as the editor.

It automatically starts you on 01field1.

Use TFGH to move to the other fields. You can drag and drop a pxpack from the kero blaster folder to quick load it.

Read readme-gx for the rest of the hotkeys.

## Editing
Several paintbrushes are available, such as rectangle and copy.


## multiplayer
Press the computer icon on the tools window. Host a server and have the other player connect. Default port is 7777.

Make sure not to edit the map before the other player joins. You'll have to load the maps in the same order too.

Undos and entity editing not supported.

