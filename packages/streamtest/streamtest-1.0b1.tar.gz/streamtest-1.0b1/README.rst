streamtest - unit test the output of standard stream
====================================================

|forthebadge|

|Build Status| |Coverage Status|

Overview
--------

The **streamtest** provides the enhanced ``unittest.TestCase`` for
testing the **output of standard stream** (``stdout``, ``stderr``).

Usage
-----

.. code:: python

    from stramtest import CatchStreamTestCase

    class StreamTestCase(CatchStreamTestCase):

        def test_stdout(self):

            with self.catch_stream("stdout") as stream:
                print "hello world"

            self.assertEqual(stream, "hello world\n")

        def test_stderr(self):

            with self.catch_stream("stderr") as stream:
                sys.stderr.write("Error!")

            self.assertEqual(stream, "Error!")

Installation
------------

::

    $ pip install streamtest


or

::

    $ git clone git@github.com:alice1017/streamtest.git
    $ cd streamtest
    $ python setup.py build install


.. |forthebadge| image:: http://forthebadge.com/images/badges/made-with-python.svg
   :target: http://forthebadge.com
.. |Build Status| image:: https://travis-ci.org/alice1017/streamtest.svg?branch=master
   :target: https://travis-ci.org/alice1017/streamtest
.. |Coverage Status| image:: https://coveralls.io/repos/github/alice1017/streamtest/badge.svg
   :target: https://coveralls.io/github/alice1017/streamtest
