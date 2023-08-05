csb43
=====


Español
-------

Herramientas para convertir ficheros en formato usado por múltiples
bancos españoles (**norma 43 del Consejo Superior Bancario** [*CSB43*]
/ **Asociación Española de Banca** [*AEB43*]) a otros formatos.


csb2format
~~~~~~~~~~

Conversor de ficheros en **CSB/AEB norma 43** a otros formatos.

Formatos soportados:

-  `OFX XML <http://www.ofx.net>`_ v1.0.3 & v2.1.1
-  `HomeBank CSV <http://homebank.free.fr/help/06csvformat.html>`_
-  *HTML*
-  *JSON*
-  *ODS*: hoja de cálculo OpenDocument
-  *CSV*, *TSV*: valores separados por coma o tabulador
-  *XLS*: hoja de cálculo de Microsoft Excel
-  *XLSX*: hoja de cálculo OOXML
-  *YAML*


Instalación:
^^^^^^^^^^^^

Todos los formatos disponibles:

::

    pip install csb43[all]


Formatos internos (ofx, ofx1, homebank) más YAML:

::

    pip install csb43[yaml]


Formatos internos (ofx, ofx1, homebank) más formatos del paquete `tablib`:

::

    pip install csb43[formats]


Opciones:
^^^^^^^^^


::

    usage: csb2format [-h] [-s] [-df] [-d DECIMAL] [--use-float] [-V]
                    [-f {csv,dbf,df,homebank,html,json,latex,ods,ofx,ofx1,tsv,xls,xlsx,yaml}]
                    [-v]
                    csbFile convertedFile

    Convierte un fichero CSB43 a otro formato

    optional arguments:
    -h, --help            show this help message and exit
    -v, --version         show program's version number and exit

    csb43 arguments:
    csbFile               fichero csb43 ('-' para entrada estándar)
    -s, --strict          modo estricto (por defecto: False)
    -df, --dayfirst       usa DDMMYY -día, mes, año- como formato de fecha al
                            interpretar los datos del fichero csb43 en lugar de
                            YYMMDD -año, mes, día- (por defecto: True)
    -d DECIMAL, --decimal DECIMAL
                            establece el número de dígitos decimales a considerar
                            en el tipo de divisa (por defecto: 2)
    --use-float           exporta cantidades monetarias usando números binarios
                            en punto flotante como último recurso (default: False)
    -V, --verbose         mostrar avisos de csb43

    output arguments:
    convertedFile         fichero de destino ('-' para salida estándar)
    -f {csv,dbf,df,homebank,html,json,latex,ods,ofx,ofx1,tsv,xls,xlsx,yaml}, --format {csv,dbf,df,homebank,html,json,latex,ods,ofx,ofx1,tsv,xls,xlsx,yaml}
                            Formato del fichero de salida (por defecto: ofx)




Ejemplos
^^^^^^^^

-  Convertir a formato OFX:

   ::

       $ csb2format transactions.csb transactions.ofx

       $ csb2format --format ofx transactions.csb transactions.ofx

   o bien

   ::

       $ csb2format transactions.csb - > transactions.ofx

   Desde una aplicación de recuperación de datos a otro fichero

   ::

       $ get_my_CSB_transactions | csb2format - transactions.ofx

-  Convertir a hoja de cálculo XLSX (Excel):

   ::

       $ csb2format --format xlsx transactions.csb transactions.xlsx


Hojas de cálculo
^^^^^^^^^^^^^^^^


Los ficheros en *ODS*, *XLS* y *XLSX* se generan a modo de libro, conteniendo
la primera hoja la información relativa a las cuentas, y las hojas
siguientes conteniendo cada una los movimientos de cada cuenta.



En Python
~~~~~~~~~


Lee un archivo *CSB43* e imprime el contenido equivalente en *OFX*

::

    :::python

    # OFX
    from csb43 import csb43, ofx

    csbFile = csb43.File(open("movimientos.csb"), strict=False)

    # imprime a stdout
    print ofx.convertFromCsb(csbFile)

Lee un archivo *CSB* e imprime el contenido equivalente a *CSV* de
*Homebank*

::

    :::python

    # OFX
    from csb43 import csb43, homebank

    csbFile = csb43.File(open("movimientos.csb"), strict=False)

    # imprime a stdout
    for line in homebank.convertFromCsb(csbFile):
        print line

Lee un archivo *CSB* e imprime el equivalente en un archivo de formato
tabular o de diccionario

::

    :::python

    # OFX
    from csb43 import csb43, formats

    csbFile = csb43.File(open("movimientos.csb"), strict=False)

    # imprime formato 'yaml' a stdout
    o = format.convertFromCsb(csbFile, 'yaml')
    print o.yaml

    # escribe a archivo en formato 'xlsx'
    o = format.convertFromCsb(csbFile, 'xlsx')
    with open("movimientos.xlsx", "wb") as f:
        f.write(o.xlsx)


--------------



English
-------

Tools for converting from the Spanish banks' format **CSB norm 43**
(*CSB43*).


csb2format
~~~~~~~~~~

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


Installing:
^^^^^^^^^^^^

All the available formats:

::

    pip install csb43[all]

Built-in formats (ofx, ofx1, homebank) plus YAML:

::

    pip install csb43[yaml]

Built-in formats (ofx, ofx1, homebank) plus formats provided by the package
`tablib`:

::

    pip install csb43[formats]


Options:
^^^^^^^^

::

    usage: csb2format [-h] [-s] [-df] [-d DECIMAL] [--use-float] [-V]
                    [-f {csv,dbf,df,homebank,html,json,latex,ods,ofx,ofx1,tsv,xls,xlsx,yaml}]
                    [-v]
                    csbFile convertedFile

    Convert a CSB43 file to another format

    optional arguments:
    -h, --help            show this help message and exit
    -v, --version         show program's version number and exit

    csb43 arguments:
    csbFile               a csb43 file ('-' for stdin)
    -s, --strict          strict mode (default: False)
    -df, --dayfirst       use DDMMYY as date format while parsing the csb43 file
                            instead of YYMMDD (default: True)
    -d DECIMAL, --decimal DECIMAL
                            set the number of decimal places for the currency type
                            (default: 2)
    --use-float           export monetary amounts using binary floating point
                            numbers as a fallback (default: False)
    -V, --verbose         show csb43 warnings

    output arguments:
    convertedFile         destination file ('-' for stdout)
    -f {csv,dbf,df,homebank,html,json,latex,ods,ofx,ofx1,tsv,xls,xlsx,yaml}, --format {csv,dbf,df,homebank,html,json,latex,ods,ofx,ofx1,tsv,xls,xlsx,yaml}
                            Format of the output file (default: ofx)



Examples
^^^^^^^^

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
^^^^^^^^^^^^


*ODS*, *XLS* and *XLSX* files are generated as books, with the first sheet
containing the accounts information, and the subsequent sheets
containing the transactions of each one of the accounts.


Using Python
~~~~~~~~~~~~


Parse a *CSB43* file and print the equivalent *OFX* file

::

    :::python

    # OFX
    from csb43 import csb43, ofx

    csbFile = csb43.File(open("movimientos.csb"), strict=False)

    # print to stdout
    print ofx.convertFromCsb(csbFile)

Parse a *CSB43* file and print the equivalent *HomeBank CSV* file

::

    :::python

    # OFX
    from csb43 import csb43, homebank

    csbFile = csb43.File(open("movimientos.csb"), strict=False)

    # print to stdout
    for line in homebank.convertFromCsb(csbFile):
        print line

Parse a *CSB43* file and print the equivalent in a tabular or
dictionary-like file format

::

    :::python

    # OFX
    from csb43 import csb43, formats

    csbFile = csb43.File(open("movimientos.csb"), strict=False)

    # print 'yaml' format to stdout
    o = format.convertFromCsb(csbFile, 'yaml')
    print o.yaml

    # write 'xlsx' format to file
    o = format.convertFromCsb(csbFile, 'xlsx')
    with open("movimientos.xlsx", "wb") as f:
        f.write(o.xlsx)

