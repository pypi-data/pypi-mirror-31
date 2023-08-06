.. default-role:: py:obj

.. include:: ../README.rst

.. only:: html

   More Examples
   ^^^^^^^^^^^^^

   For more examples, have a look at the :doc:`examples`.

.. include:: ../CONTRIBUTING.rst

.. default-role:: any

API Documentation
-----------------

.. automodule:: sounddevice
   :members:
   :undoc-members:
   :exclude-members: RawInputStream, RawOutputStream, RawStream,
                     InputStream, OutputStream, Stream,
                     CallbackFlags, CallbackStop, CallbackAbort,
                     PortAudioError, DeviceList,
                     AsioSettings, CoreAudioSettings, WasapiSettings

.. autoclass:: Stream
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: InputStream

.. autoclass:: OutputStream

.. autoclass:: RawStream
   :members: read, write

.. autoclass:: RawInputStream

.. autoclass:: RawOutputStream

.. autoclass:: DeviceList

.. autoclass:: CallbackFlags
   :members:

.. autoclass:: CallbackStop

.. autoclass:: CallbackAbort

.. autoclass:: PortAudioError

.. autoclass:: AsioSettings

.. autoclass:: CoreAudioSettings

.. autoclass:: WasapiSettings

.. only:: html

   Index
   -----
 
   :ref:`genindex`

Version History
---------------

.. default-role:: py:obj

.. include:: ../NEWS.rst

.. default-role::
