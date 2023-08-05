
Converter
==========

Convert a **CSB/AEB norm 43** file to other file formats.

Supported formats:

- OFX v1.0.3 (SGML) & v2.1.1 (XML)
- `HomeBank CSV <http://homebank.free.fr/help/06csvformat.html>`_
- *HTML*
- *JSON*
- *ODS*: OpenDocument spreadsheet
- *CSV*, *TSV*: comma- or tab- separated values
- *XLS*: Microsoft Excel spreadsheet
- *XLSX*: OOXML spreadsheet
- *YAML*

Options:
-----------

::

    usage: csb2format [-h] [-s] [-df] [-d DECIMAL]
                  [-f {csv,homebank,html,json,ods,ofx,ofx1,tsv,xls,xlsx,yaml}] [-v]
                  csbFile convertedFile

    Convert a CSB43 file to another format

    positional arguments:
    csbFile               a csb43 file ('-' for stdin)
    convertedFile         destination file ('-' for stdout)

    optional arguments:
    -h, --help            show this help message and exit
    -s, --strict          strict mode
    -df, --dayfirst       use DDMMYY as date format while parsing the csb43 file
                            instead of YYMMDD (default: True)
    -d DECIMAL, --decimal DECIMAL
                            set the number of decimal places for the currency type
                            (default: 2)
    -f {csv,homebank,html,json,ods,ofx,ofx1,tsv,xls,xlsx,yaml}, --format {csv,homebank,html,json,ods,ofx,ofx1,tsv,xls,xlsx,yaml}
                            Format of the output file (default: ofx)

Examples
----------

- Converting to OFX format:

    ::

        $ csb2format transactions.csb transactions.ofx

        $ csb2format --format ofx transactions.csb transactions.ofx

    or

    ::

        $ csb2format transactions.csb - > transactions.ofx

    From another app to file

    ::

        $ get_my_CSB_transactions | csb2format - transactions.ofx

- Converting to XLSX spreadsheet format:

    ::

        $ csb2format --format xlsx transactions.csb transactions.xlsx

Spreadsheets
-------------


*ODS*, *XLS* and *XLSX* files are generated as books, with the first sheet
containing the accounts information, and the subsequent sheets
containing the transactions of each one of the accounts.
