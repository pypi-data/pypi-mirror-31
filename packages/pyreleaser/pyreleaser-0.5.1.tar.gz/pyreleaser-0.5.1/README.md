# PyReleaser

[![Version](https://img.shields.io/pypi/v/pyreleaser.svg)](https://pypi.python.org/pypi/pyreleaser)
[![License](https://img.shields.io/pypi/l/pyreleaser.svg)](https://pypi.python.org/pypi/pyreleaser)
[![PythonVersions](https://img.shields.io/pypi/pyversions/pyreleaser.svg)](https://pypi.python.org/pypi/pyreleaser)
[![Build](https://travis-ci.org/pior/pyreleaser.svg?branch=master)](https://travis-ci.org/pior/pyreleaser)

Simple command to release your Python project to PyPI.

Release flow:
- update setup.py version
- `git tag -a`
- `git push`

Upload flow:
- `python setup.py sdist bdist_wheel`
- `twine upload`


## Install

```shell
$ pip install 'pyreleaser > 0.5.1'
```


## Usage

Create the release:
```bash
$ pyreleaser create 0.5.1
🔸  Update version in setup.py
🔸  Commit the release
[master 1b206aa] Release v0.5.1
 1 file changed, 1 insertion(+), 1 deletion(-)
🔸  Tag the release: v0.5.1

🔔  Don't forget to push with: git push --follow-tags
```

Upload to PyPI:
```bash
$ pyreleaser upload
🔸  Build distributions
🔸  Upload to PyPI
```
