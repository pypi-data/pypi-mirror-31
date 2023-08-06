# Python Client for Pilosa

<a href="https://github.com/pilosa"><img src="https://img.shields.io/badge/pilosa-0.9-blue.svg"></a>
<a href="https://pypi.python.org/pypi/pilosa"><img src="https://img.shields.io/pypi/v/pilosa.svg?maxAge=2592&updated=2"></a>
<a href="http://pilosa.readthedocs.io/en/latest/?badge=latest"><img src="https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat"></A>
<a href="https://travis-ci.org/pilosa/python-pilosa"><img src="https://api.travis-ci.org/pilosa/python-pilosa.svg?branch=master"></a>
<a href="https://coveralls.io/github/pilosa/python-pilosa?branch=master"><img src="https://coveralls.io/repos/github/pilosa/python-pilosa/badge.svg?branch=master"></a>

<img src="https://www.pilosa.com/img/ce.svg" style="float: right" align="right" height="301">

Python client for Pilosa high performance distributed bitmap index.

## What's New?

See: [CHANGELOG](CHANGELOG.md)

## Requirements

* Python 2.7 and higher or Python 3.4 and higher.

## Install

Pilosa client is on [PyPI](https://pypi.python.org/pypi/pilosa). You can install the library using `pip`:

```
pip install pilosa
```

## Usage

### Quick overview

Assuming [Pilosa](https://github.com/pilosa/pilosa) server is running at `localhost:10101` (the default):

```python
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
```

## Documentation

### Data Model and Queries

See: [Data Model and Queries](docs/data-model-queries.md)

### Executing Queries

See: [Server Interaction](docs/server-interaction.md)

### Importing and Exporting Data

See: [Importing and Exporting Data](docs/imports.md)

## Contributing

See: [CONTRIBUTING](CONTRIBUTING.md)

## License

See: [LICENSE](LICENSE)
