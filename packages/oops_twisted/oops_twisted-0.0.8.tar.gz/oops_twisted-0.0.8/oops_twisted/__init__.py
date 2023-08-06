#
# Copyright (c) 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Lesser General Public License version 3 (see the file LICENSE).

"""OOPS error reports for Twisted.

The oops_twisted package provides integration glue between logged twisted
errors (via the twisted.log api) and the oops error reporting system
(http://pypi.python.org/pypi/oops).

Dependencies
============

* Python 2.6+

* oops (http://pypi.python.org/pypi/oops)

* Twisted

Testing Dependencies
====================

* subunit (http://pypi.python.org/pypi/python-subunit) (optional)

* testtools (http://pypi.python.org/pypi/testtools)

Usage
=====

OOPS Configuration
++++++++++++++++++

* Setup your configuration::

  >>> from oops_twisted import Config
  >>> config = Config()

Note that you will probably want at least one publisher, or your reports will
be silently discarded.

* When adding publishers, either wrap 'normal' OOPS publishers in deferToThread
  or similar, or use native Twisted publishers. For instance::

 >>> from functools import partial
 >>> config.publisher = partial(deferToThread, blocking_publisher)

 A helper 'defer_publisher' is supplied to do this for your convenience.

Catching log.err calls
++++++++++++++++++++++

* create an OOPS log observer::

 >>> from oops_twisted import OOPSObserver
 >>> observer = OOPSObserver(config)

* And enable it::

 >>> from twisted.log import addObserver
 >>> addObserver(observer)

* This is typically used to supplement regular logging, e.g. you might
  initialize normal logging to a file first::

 >>> twisted.log.startLogging(logfile)

The OOPSObserver will discard all non-error log messages, and convert error log
messages into OOPSes using the oops config.

Optionally, you can provide OOPSObserver with a second observer to delegate
too. Any event that is not converted into an OOPS is passed through unaltered.
Events that are converted to OOPSes have a new event second to the second
observer which provides the OOPS id and the failure name and value::

 >>> observer = OOPSObserver(config, twisted.log.PythonLoggingObserver().emit)

If the OOPS config has no publishers, the fallback will receive unaltered
failure events (this stops them getting lost). If there are publishers but the
OOPS is filtered, the fallback will not be invoked at all (this permits e.g.
rate limiting of failutes via filters).

Creating OOPSes without using log.err
+++++++++++++++++++++++++++++++++++++

You can directly create an OOPS if you have a twisted failure object::

 >>> from twisted.python.failure import Failure
 >>> report = config.create(dict(twisted_failure=Failure()))
 >>> config.publish(report)

Extending WSGI
++++++++++++++

oops_twisted supports an extended WSGI contract where if the returned iterator
for the body implements t.w.i.IBodyProducer, then the iterator that
oops_twisted's WSGI wrapper returns will also implement IBodyProducer. This is
useful with a customised Twisted WSGI resource that runs IBodyProducer
iterators in the IO loop, rather than using up a threadpool thread. To use this
pass tracker=oops_twisted.wsgi.body_producer_tracker when calling
oops_wsgi.make_app. Note that a non-twisted OOPS Config is assumed because
the WSGI protocol is synchronous: be sure to provide the oops_wsgi make_app
with a non-twisted OOPS Config.

If you are publishing with native OOPS publishers you may want to write a small
synchronous publish-to-an-internal queue as you cannot use
t.i.t.blockingCallFromThread: the WSGI protocol permits start_response to be
called quite late, which may happen after an IBodyProducer has been returned to
the WSGI gateway and all further code will be executing in the reactor thread.
Specifically the call to startProducing may trigger start_response being called
before the first write() occurs; and the call to start_response may trigger an
OOPS being published if:
 - it contains an exc_info value
 - it has a status code matching the oops-on-status code values
 - (in future) the response takes too long to start flowing
Another route to exceptions is in startProducing itself, which may error, with
similar consequences in that the oops config must be called into, and it has to
be compatible with the config for start_response handling. If there is a need
to address this, oops_twisted could take responsibility for exception handling
in the IBodyProducer code path, with the cost of needing a second OOPS config
- a native Twisted one.
"""


from __future__ import absolute_import, print_function

# same format as sys.version_info: "A tuple containing the five components of
# the version number: major, minor, micro, releaselevel, and serial. All
# values except releaselevel are integers; the release level is 'alpha',
# 'beta', 'candidate', or 'final'. The version_info value corresponding to the
# Python version 2.0 is (2, 0, 0, 'final', 0)."  Additionally we use a
# releaselevel of 'dev' for unreleased under-development code.
#
# If the releaselevel is 'alpha' then the major/minor/micro components are not
# established at this point, and setup.py will use a version of next-$(revno).
# If the releaselevel is 'final', then the tarball will be major.minor.micro.
# Otherwise it is major.minor.micro~$(revno).
__version__ = (0, 0, 8, 'beta', 0)

__all__ = [
    'Config',
    'convert_result_to_list',
    'defer_publisher',
    'OOPSObserver',
    'publish_to_many',
    'publish_with_fallback',
    ]

from oops_twisted.config import (
    Config,
    defer_publisher,
    )
from oops_twisted.log import OOPSObserver
from oops_twisted.publishers import (
    convert_result_to_list,
    publish_to_many,
    publish_with_fallback,
    )
