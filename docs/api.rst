.. currentmodule:: lightspeed

API Reference
===============

The following section outlines the API of lightspeed.py.

.. note::

    This module uses the Python logging module to log diagnostic and errors
    in an output independent way.  If the logging module is not configured,
    these logs will not be output anywhere.  See :ref:`logging_setup` for
    more information on how to set up and use the logging module with
    lightspeed.py.

Version Related Info
---------------------

There are two main ways to query version information about the library. For guarantees, check :ref:`version_guarantees`.

.. data:: version_info

    A named tuple that is similar to :obj:`py:sys.version_info`.

    Just like :obj:`py:sys.version_info` the valid values for ``releaselevel`` are
    'alpha', 'beta', 'candidate' and 'final'.

.. data:: __version__

    A string representation of the version. e.g. ``'1.0.0rc1'``. This is based
    off of :pep:`440`.

Clients
--------

Client
~~~~~~~

.. attributetable:: Client

Identifier
~~~~~~~~~~
.. autoclass:: lightspeed.abc.Identifier()
    :members:

Messageable
~~~~~~~~~~~
.. autoclass:: lightspeed.abc.Messageable()
    :members:

PartialCategory
~~~~~~~~~~~~~~~
.. attributetable:: PartialCategory

.. autoclass:: PartialCategory()
    :members:

Category
~~~~~~~~
.. attributetable:: Category

.. autoclass:: Category()
    :members:

Invite
~~~~~~
.. attributetable:: Invite

.. autoclass:: Invite()
    :members:

PartialMessage
~~~~~~~~~~~~~~
.. attributetable:: PartialMessage

.. autoclass:: PartialMessage()
    :members:

Message
~~~~~~~
.. attributetable:: Message

.. autoclass:: Message()
    :members:

Object
~~~~~~
.. attributetable:: Object

.. autoclass:: Object
    :members:

Region
~~~~~~
.. attributetable:: Region

.. autoclass:: Region()
    :members:

Ban
~~~
.. attributetable:: Ban

.. autoclass:: Ban()
    :members:

PartialStream
~~~~~~~~~~~~~
.. attributetable:: PartialStream

.. autoclass:: PartialStream()
    :members:

Live
~~~~
.. attributetable:: Live

.. autoclass:: Live()
    :members:

Stream
~~~~~~
.. attributetable:: Stream

.. autoclass:: Stream()
    :members:
    :inherited-members:

LargeStream
~~~~~~~~~~~
.. attributetable:: LargeStream

.. autoclass:: LargeStream()
    :members:
    :inherited-members:

SocialLink
~~~~~~~~~~
.. attributetable:: SocialLink

.. autoclass:: SocialLink
    :members:

PartialUser
~~~~~~~~~~~
.. attributetable:: PartialUser

.. autoclass:: PartialUser()
    :members:

User
~~~~
.. attributetable:: User

.. autoclass:: User()
    :members:
    :inherited-members:

UserBan
~~~~~~~
.. attributetable:: UserBan

.. autoclass:: UserBan()
    :members:

ClientUser
~~~~~~~~~~
.. attributetable:: ClientUser

.. autoclass:: ClientUser()
    :members:
    :inherited-members:

.. data:: MISSING
    :module: lightspeed.utils

    A type safe sentinel used in the library to represent something as missing. Used to distinguish from ``None`` values.
    
Enumerations
-------------

The API provides some enumerations for certain types of strings to avoid the API
from being stringly typed in case the strings change in the future.

All enumerations are subclasses of an internal class which mimics the behaviour
of :class:`enum.Enum`.

.. class:: Controller

    Represents how you should connect to this live stream.


    .. versionadded:: 2.4

    .. attribute:: inhouse

        You must connect in house.

    .. attribute:: mist
        
        (???) TODO

Exceptions
------------

The following exceptions are thrown by the library.

.. autoexception:: LightspeedException

.. autoexception:: ClientException

.. autoexception:: LoginFailure

.. autoexception:: HTTPException
    :members:

.. autoexception:: RateLimited
    :members:

.. autoexception:: Forbidden

.. autoexception:: NotFound

.. autoexception:: LightspeedServerError

Exception Hierarchy
~~~~~~~~~~~~~~~~~~~~~

.. exception_hierarchy::

    - :exc:`Exception`
        - :exc:`LightspeedException`
            - :exc:`ClientException`
                - :exc:`LoginFailure`
            - :exc:`HTTPException`
                - :exc:`Forbidden`
                - :exc:`NotFound`
                - :exc:`LightspeedServerError`
            - :exc:`RateLimited`