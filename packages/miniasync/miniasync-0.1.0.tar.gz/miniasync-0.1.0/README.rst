miniasync
=========

**miniasync** is a small library build on top of asyncio_ to faciliate running small portions of asynchronous code in an otherwise synchronous application.

A typical use case is an application which is build as a synchronous application, but at some point needs to make an http request to two different web services and await the results before continuing. In synchronous Python you'd have to do each request in turn - **miniasync** makes it easier to run both requests in parallel without having to write asyncio_ boilerplate code.

See the `documentation on readthedocs`_ for examples and API.

.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _documentation on readthedocs: https://miniasync.readthedocs.io

License
-------

Copyright © 2018, Alice Heaton. Released under the `LGPL 3 License`_

.. _LGPL 3 License: https://www.gnu.org/licenses/lgpl-3.0.html
