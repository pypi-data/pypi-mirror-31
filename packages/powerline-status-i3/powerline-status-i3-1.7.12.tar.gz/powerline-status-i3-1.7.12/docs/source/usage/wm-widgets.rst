**********************
Window manager widgets
**********************

Awesome widget
==============

.. note:: Powerline currently only supports awesome 3.5 and 4+.

.. note:: The Powerline widget will spawn a shell script that runs in the
   background and updates the statusline with ``awesome-client``.

Add the following to :file:`rc.lua`, where ``{repository_root}`` is the absolute
path to Powerline installation directory (see :ref:`repository root
<repository-root>`):

.. code-block:: lua

   package.path = package.path .. ';{repository_root}/powerline/bindings/awesome/?.lua'
   require('powerline')

Then add the ``powerline_widget`` to ``wibox``:

.. code-block:: lua

   -- awesome3.5
   right_layout:add(powerline_widget)

   -- awesome4+
   s.mywibox:setup {
   ...
     { -- Right widgets
       ...
       powerline_widget,
     },
   }

Qtile widget
============

Add the following to :file:`~/.config/qtile/config.py`:

.. code-block:: python

   from libqtile.bar import Bar
   from libqtile.config import Screen
   from libqtile.widget import Spacer

   from powerline.bindings.qtile.widget import PowerlineTextBox

   screens = [
       Screen(
           top=Bar([
                   PowerlineTextBox(update_interval=2, side='left'),
                   Spacer(),
                   PowerlineTextBox(update_interval=2, side='right'),
               ],
               35 # width
           ),
       ),
   ]

.. _lemonbar-usage:

lemonbar (formerly bar-aint-recursive)
======================================

To run the bar simply start the binding script:

    powerline-lemonbar

You can specify options to be passed to ``lemonbar`` after ``--``, like so:

    powerline-lemonbar -- -a 40 -f 'DejaVu Sans Mono-11' -f 'PowerlineSymbols-12' -f 'FontAwesome-11'"


To run with i3, simply ``exec`` this in the i3 config file and set the ``--i3`` switch:

    exec powerline-lemonbar --i3

Further, increase the number of clickable areas to some apporpriate number (default is 10):

    exec powerline-lemonbar --i3 -- -a 40

Running the binding in i3-mode will require `i3ipc <https://github.com/acrisci/i3ipc-python>`_
(or the outdated `i3-py <https://github.com/ziberna/i3-py>`_).

See the `lemonbar documentation <https://github.com/LemonBoy/bar>`_ for more
information and options.
=======

All ``powerline-lemonbar`` arguments:

.. automan:: powerline.commands.lemonbar
   :prog: powerline-lemonbar
   :minimal: true

