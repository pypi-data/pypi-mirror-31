# ElectronBonder
A client library for working with the Project Electron APIs.

## Requirements
ElectronBonder has the following requirements.

- Python 3.4 or higher
- ability to install packages via pip ([Pipenv](https://docs.pipenv.org/) is recommended for development)

## Installation
The easiest way to install ElectronBonder is via pip:

      pip3 install ElectronBonder

You'll need an internet connection to fetch ElectronBonder's dependencies.

## Usage
To start, you must authorize against the application:

``` python
from electronbonder.client import ElectronBond

client = ElectronBond(baseurl="http://my.aspace.backend.url.edu:4567",
                      username="admin",
                      password="admin")
client.authorize()
```

The authorization token for that user is then sent in requests to that application's endpoints.

## Configuration

As per the example above, the client object should be configured by passing it arguments during creation.

Allowed configuration values are:

| **Setting** | **Description**                                                               |
|-------------|-------------------------------------------------------------------------------|
| baseurl     | The location (including port if not on port 80) of the application's API root |
| username    | Username for authorization                                                    |
| password    | Password for authorization                                                    |
