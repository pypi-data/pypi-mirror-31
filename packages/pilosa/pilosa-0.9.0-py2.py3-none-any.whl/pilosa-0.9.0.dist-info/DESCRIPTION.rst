Python Client for Pilosa
========================

Python client for Pilosa high performance distributed bitmap index.

What's New?
-----------

See: `CHANGELOG <CHANGELOG.md>`__

Requirements
------------

-  Python 2.7 and higher or Python 3.4 and higher.

Install
-------

Pilosa client is on `PyPI <https://pypi.python.org/pypi/pilosa>`__. You
can install the library using ``pip``:

::

    pip install pilosa

Usage
-----

Quick overview
~~~~~~~~~~~~~~

Assuming `Pilosa <https://github.com/pilosa/pilosa>`__ server is running
at ``localhost:10101`` (the default):

.. code:: python

    import pilosa

    # Create the default client
    client = pilosa.Client()

    # Retrieve the schema
    schema = client.schema()

    # Create an Index object
    myindex = schema.index("myindex")

    # Create a Frame object
    myframe = myindex.frame("myframe")

    # make sure the index and frame exists on the server
    client.sync_schema(schema)

    # Send a SetBit query. PilosaError is thrown if execution of the query fails.
    client.query(myframe.setbit(5, 42))

    # Send a Bitmap query. PilosaError is thrown if execution of the query fails.
    response = client.query(myframe.bitmap(5))

    # Get the result
    result = response.result

    # Act on the result
    if result:
        bits = result.bitmap.bits
        print("Got bits: ", bits)

    # You can batch queries to improve throughput
    response = client.query(
        myindex.batch_query(
            myframe.bitmap(5),
            myframe.bitmap(10),
        )    
    )
    for result in response.results:
        # Act on the result
        print(result)

Documentation
-------------

Data Model and Queries
~~~~~~~~~~~~~~~~~~~~~~

See: `Data Model and Queries <docs/data-model-queries.md>`__

Executing Queries
~~~~~~~~~~~~~~~~~

See: `Server Interaction <docs/server-interaction.md>`__

Importing and Exporting Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See: `Importing and Exporting Data <docs/imports.md>`__

Contributing
------------

See: `CONTRIBUTING <CONTRIBUTING.md>`__

License
-------

See: `LICENSE <LICENSE>`__


