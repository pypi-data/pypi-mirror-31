Yugioh Bot
----------

|Join the chat at https://gitter.im/Yugioh-bot/Lobby| |Discord|
|Software License| |Build Status| |Coverage Status| |Quality Score|

Bot to help with those npc in Yugioh Duel Links.

Features
--------

-  Auto-duel npc
-  Collect worlds rewards
   |Example Install|

Prerequisites
-------------

| Have Nox installed (https://www.bignox.com)
| -- Note: Windows 10 Users make sure to disable Hyper-V in window
  services otherwise BSoD errors will occur.
| Python 3.5 or 3.6 (https://www.python.org/downloads/,
  https://www.anaconda.com/download/)

Install
-------

Via git

.. code:: bash

    $ git clone https://github.com/will7200/Yugioh-bot
    $ cd Yugioh-bot
    $ pip install -r requirements.txt (or use conda if using)
    $ pip install -r install_requirements.txt
    $ python install.py

Via zip file -- Unzip Contents

.. code:: bash

    $ cd Yugioh-bot
    $ pip install -r requirements.txt (or use conda if using)
    $ pip install -r install_requirements.txt
    $ python install.py

If you are using conda, here is a powershell script that will help

.. code:: powershell

    $ Get-Content requirements.txt | ForEach-Object {
    conda install --yes $_
    }

Afterwards
----------

Skip to 6 on this list if you used python install.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Install tesseract (http://3.onj.me/tesseract/)
   If the above link is giving issues or is slow: Tesseract at UB
   Mannheim (https://github.com/UB-Mannheim/tesseract/wiki)
   -- Note: Testings occured on the 3.05.01 version
2. opencv\_python‑3.3.1+contrib and cv2+contrib 3.2.0 tested
   (http://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv) -- Note: pypi
   package will now install cv2+contrib from requirements.txt
3. Copy downloaded tesseract folder into bin:raw-latex:`\tess`
4. Copy
   C::raw-latex:`\Users`:raw-latex:`\USER`\_NAME:raw-latex:`\AppData`:raw-latex:`\Roaming`:raw-latex:`\Nox`:raw-latex:`\bin`:raw-latex:`\nox`\_adb.exe
   as adb.exe into bin directory
5. Copy
   C::raw-latex:`\Users`:raw-latex:`\USER`\_NAME:raw-latex:`\AppData`:raw-latex:`\Roaming`:raw-latex:`\Nox`:raw-latex:`\bin`:raw-latex:`\AdbWinApi`.dll
   into bin directory
6. Set Nox as 480x800 phone
7. Download Yugioh app
8. Setup Yugioh app, link, etc... (first time only)

Usage
-----

To Start The Bot

.. code:: bash

    $ python main.py bot -s

Generate Config File -- Only Needed if you did not git clone master

.. code:: bash

    $ python main.py config --generate-config {optional --file-path path/to/file/config.ini}

The bot creates a file for runtime purposes that is specified in the
config file name runtimepersistence under the bot section.

The following values can be changed during runtime that will control the
bot until the ui has been made. ["run\_now", "stop", "next\_run\_at"]

| run\_now: if the bot is currently stopped it will schedule a run
  immediately
| stop: if the bot is currently running it will halt execution
| next\_run\_at: will schedule a run at the specified time, if currently
  running it will remove the current job in place of the new one

GUI

.. code:: bash

    $ pythonw main.py gui -s

| This will start the bot with gui controls.
| So far the following signals have been implemented: \* Stop \* Run Now
| |Image of Gui|

Wakatime
--------

Check out what files I'm working on through
`WakaTime <https://wakatime.com/@will2700/projects/fofjloaywu>`__

Change log
----------

Please see `CHANGELOG <CHANGELOG.md>`__ for more information on what has
changed recently.

Security
--------

If you discover any security related issues, please open a issue with
"`Security <#security>`__" as the prefix.

Credits
-------

-  `will7200 <https://github.com/will7200>`__

-  `All Contributors <../../contributors>`__

-  tellomichmich (https://github.com/tellomichmich/PokeNoxBot) for the
   idea and some basic guides for nox usage with python ## License

The MIT License (MIT). Please see `License File <LICENSE>`__ for more
information.

.. |Join the chat at https://gitter.im/Yugioh-bot/Lobby| image:: https://badges.gitter.im/Yugioh-bot/Lobby.svg
   :target: https://gitter.im/Yugioh-bot/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
.. |Discord| image:: https://img.shields.io/discord/392538066633359360.svg?colorB=0082ff&style=flat
   :target: https://discord.gg/PGWedhf
.. |Software License| image:: https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat-square
   :target: LICENSE
.. |Build Status| image:: https://img.shields.io/travis/:vendor/:package_name/master.svg?style=flat-square
   :target: https://travis-ci.org/:vendor/:package_name
.. |Coverage Status| image:: https://coveralls.io/repos/github/will7200/Yugioh-bot/badge.svg?branch=master
   :target: https://coveralls.io/github/will7200/Yugioh-bot?branch=master
.. |Quality Score| image:: https://img.shields.io/scrutinizer/g/:vendor/:package_name.svg?style=flat-square
   :target: https://scrutinizer-ci.com/g/:vendor/:package_name
.. |Example Install| image:: https://media.giphy.com/media/3oFzm8CBfGBdhKRms8/giphy.gif
.. |Image of Gui| image:: https://image.ibb.co/ccQ79b/yugioh_duel_bots_gui.png

