========
nodepool
========

.. _nodepool_3.0.1:

3.0.1
=====

.. _nodepool_3.0.1_Prelude:

Prelude
-------

.. releasenotes/notes/initial-note-f7414710196b7198.yaml @ b'e457f0c6da16f39b315d53e0d16dbec14a9c9388'

Initial release note. This note should be removed as soon as we have a real one.


.. _nodepool_3.0.1_New Features:

New Features
------------

.. releasenotes/notes/diskimage-connection-port-f53b0a9c910cb393.yaml @ b'687f120b3c21b527c217a734144e105d7daead76'

- The connection port can now be configured in the provider diskimages
  section.

.. releasenotes/notes/static-driver-windows-cf80096636dbb428.yaml @ b'da95a817bbc742dbab587953b542686a4c375c89'

- Added support for configuring windows static nodes. A static node can now
  define a ``connection-type``. The ``ssh-port`` option has been renamed
  to ``connection-port``.


.. _nodepool_3.0.1_Deprecation Notes:

Deprecation Notes
-----------------

.. releasenotes/notes/static-driver-windows-cf80096636dbb428.yaml @ b'da95a817bbc742dbab587953b542686a4c375c89'

- ``ssh-port`` in static node config is deprecated. Please update config to
  use ``connection-port`` instead.

