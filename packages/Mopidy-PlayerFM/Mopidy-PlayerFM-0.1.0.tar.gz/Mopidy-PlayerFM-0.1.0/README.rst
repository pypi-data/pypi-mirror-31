***************
Mopidy-PlayerFM
***************

.. image:: https://img.shields.io/pypi/v/Mopidy-PlayerFM.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-PlayerFM/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/travis/konsulko/mopidy-playerfm/master.svg?style=flat
    :target: https://travis-ci.org/konsulko/mopidy-playerfm
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/konsulko/mopidy-playerfm/master.svg?style=flat
   :target: https://coveralls.io/github/konsulko/mopidy-playerfm
   :alt: Test coverage

`Mopidy <http://www.mopidy.com/>`_ extension for playing music from
`PlayerFM <https://player.fm/>`_.


Installation
============

Install by running::

    pip install Mopidy-PlayerFM


Configuration
=============

Before starting Mopidy, you may add the optional username/password
configuration for PlayerFM to your Mopidy configuration file::

    [playerfm]
    username = myusername
    password = mypassword


Usage
=====

The extension is enabled by default if all dependencies are
available. When username or password are not present, you may
browse the featured podcasts and add/play them. When authenticated
to a PlayerFM account, your subscribed podcasts are synced to a
**PlayerFM - Subscribed Podcasts** playlist.


Project resources
=================

- `Source code <https://github.com/konsulko/mopidy-playerfm>`_
- `Issue tracker <https://github.com/konsulko/mopidy-playerfm/issues>`_


Credits
=======

- Original author: `Matt Porter <https://github.com/ohporter>`_
- Current maintainer: `Matt Porter <https://github.com/ohporter>`_


Changelog
=========

v0.1.0 (2018-04-27)
----------------------------------------

- Initial release
