# Isolated reference validation

These checks exercise selected behavior from the non-active references. They
do not add either reference to the product runtime or approve its deployment.

## ReClip

Use a separate Python environment with the reference requirements installed:

```sh
python -m unittest discover -s tests/references -p 'test_reclip.py' -v
```

The tests copy `app.py` and its templates into a temporary directory before
importing them. Subprocesses and download threads are mocked; only synthetic
temporary files are served or cleaned up. No live platform request is made.

## MediaGrabber

Copy the reference to a separate workspace and install its frozen dependencies
there with `npm ci --ignore-scripts`. Point the test at that isolated copy:

```sh
MEDIA_GRABBER_VALIDATION_ROOT=/absolute/path/to/isolated/mediagrabber \
  node --test tests/references/mediagrabber.test.cjs
```

The suite transpiles and loads only the reviewed HLS, DASH, quality and RPC
modules. It never starts the native host, installer, browser hooks or downloader.
Fetch errors are simulated. Passing these checks does not establish live-site,
browser-store, native-registration or production-service compatibility.
