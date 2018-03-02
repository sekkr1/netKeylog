.. netKeylog documentation master file, created by
   sphinx-quickstart on Sun Nov 05 22:51:26 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to netKeylog's documentation!
=========================================

netKeylog is A host-controller pair software enabling you to remotely monitor keystrokes and context of clients in your local area network.

There's a client that runs in the background of the host machine recording keystrokes, where they were sent and their locale and you can set it up to run on startup. The client broadcasts itself to the manager.

And there's a controller that pools all the hosts in the network and enables the supervisor to view the hosts, fetch and view their data using a rich user interface.

Parts
=====

.. toctree::
   :maxdepth: 4

   client
   controller
   ui
   utils



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
