.. image:: https://travis-ci.org/morganwahl/packrat.svg?branch=master
    :target: https://travis-ci.org/morganwahl/packrat

.. image:: https://coveralls.io/repos/github/morganwahl/packrat/badge.svg?branch=master
    :target: https://coveralls.io/github/morganwahl/packrat?branch=master

.. image:: https://circleci.com/gh/morganwahl/packrat.svg?style=svg
    :target: https://circleci.com/gh/morganwahl/packrat

.. image:: https://codecov.io/gh/morganwahl/packrat/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/morganwahl/packrat

Serve existing files you already have lying around. "Upload" them with a Django backend.

This package has two components:
- packrat daemon: A tiny Django project to serve some files from a directory at URLs based on a hash of their contents.
- A Django storage backend that "uploads" files by simply computing their hash and just assuming they already exist on a packrat daemon.

To serve files from the daemon:

1. Run ``packrat-add <directory>`` to recursively add all the files in a directory to the packrat index. This will read their contents to compute hashes.
2. Run ``packrat-daemon``.

To use the storage backend, add it to your settings like this:

BACKENDS = (
    'packrat.storage', {'URL': '<URL of the daemon you ran above>'}
)

'packrat.widget.FileUpload' is a file "uploading" widget that simply computes the hash of file data client-side, then send the has to the server.

WHY?

You have some potentially large files someplace you want to make use of in a web-app without having to copy them around.
