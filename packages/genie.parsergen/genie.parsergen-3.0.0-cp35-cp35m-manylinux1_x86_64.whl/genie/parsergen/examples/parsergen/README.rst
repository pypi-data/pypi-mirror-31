parsergen - CLI show command parsing classes for pyATS.
=======================================================


.. note::

        For better viewing/reading of this document, use restview_.
        
        .. _restview: https://pypi.python.org/pypi/restview
        
        For example::
        
            restview -l 0:8080 README.rst

        And then browse to http://your_machine:8080


Please refer to the parsergen `online documentation`_.

.. _online documentation: http://wwwin-pyats.cisco.com/cisco-shared/html/parsergen/docs/index.html


How to run sample pyATS job against various reference platforms:
----------------------------------------------------------------
::

    cd examples/parsergen/pyAts
    cat README


How to run standalone parsergen demonstrations:
-----------------------------------------------
::

    cd examples/parsergen/pyAtsStandaloneUt
    python cli_command_formatting_example.py
    python tabular_parser_subclass.py
    python nontabular_parser_vios.py
    python nontabular_parser_viosxe.py
    python nontabular_parser_vnxos.py
    python nontabular_parser_xrvr.py


How to run unit tests:
----------------------
::

    cd <pyats_root>/lib/py*/site-packages/parsergen/tests
    python -m unittest discover
