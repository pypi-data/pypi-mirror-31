.. :changelog:

Release History
---------------

0.3.0 (2018-04-26)
++++++++++++++++++

- Adds optional ``encoding`` param to ``upload`` method so that encoding may be provided for non utf-8 files to be uploaded, without this ``UnicodeDecodeError`` would raise.


0.2.0 (2018-04-26)
++++++++++++++++++

- Adds ``mkdir`` client method.
- Bugfix where pathlib Paths could not be used as client parameters.


0.1.2 (2018-04-20)
++++++++++++++++++

- Bugfix for issue where if the server responded with non-JSON ``JSONDecodeError`` would raise, now raises ``BrickFTPError``.


0.1.1 (2018-04-19)
++++++++++++++++++

- Bugfix for issue where Forbidden would be raised for the inital request if the authenticated user is not the account holder username.


0.1.0 (2018-04-11)
++++++++++++++++++

- Initial release
