[![](https://img.shields.io/pypi/pyversions/slicedict.svg?maxAge=86400)](https://pypi.org/pypi/slicedict/)
[![](https://img.shields.io/pypi/v/slicedict.svg?maxAge=86400)](https://pypi.org/pypi/slicedict/)
[![](https://img.shields.io/badge/libraries.io-slicedict-green.svg)](https://libraries.io/pypi/slicedict)

[![CodeFactor](https://www.codefactor.io/repository/github/looking-for-a-job/slicedict.py/badge)](https://www.codefactor.io/repository/github/looking-for-a-job/slicedict.py)
[![CodeClimate](https://codeclimate.com/github/looking-for-a-job/slicedict.py/badges/gpa.svg)](https://codeclimate.com/github/looking-for-a-job/slicedict.py)
[![Scrutinizer](https://scrutinizer-ci.com/g/looking-for-a-job/slicedict.py/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/looking-for-a-job/slicedict.py/)
[![BetterCodeHub](https://bettercodehub.com/edge/badge/looking-for-a-job/slicedict.py?branch=master)](https://bettercodehub.com/results/looking-for-a-job/slicedict.py)
[![Sonarcloud](https://sonarcloud.io/api/project_badges/measure?project=slicedict.py&metric=code_smells)](https://sonarcloud.io/dashboard?id=slicedict.py)

[![Codecov](https://codecov.io/gh/looking-for-a-job/slicedict.py/branch/master/graph/badge.svg)](https://codecov.io/gh/looking-for-a-job/slicedict.py)
[![CircleCI](https://circleci.com/gh/looking-for-a-job/slicedict.py/tree/master.svg?style=svg)](https://circleci.com/gh/looking-for-a-job/slicedict.py/tree/master)
[![Scrutinizer](https://scrutinizer-ci.com/g/looking-for-a-job/slicedict.py/badges/build.png?b=master)](https://scrutinizer-ci.com/g/looking-for-a-job/slicedict.py/)
[![Semaphore CI](https://semaphoreci.com/api/v1/looking-for-a-job/slicedict-py/branches/master/shields_badge.svg)](https://semaphoreci.com/looking-for-a-job/slicedict-py)
[![Travis](https://api.travis-ci.org/looking-for-a-job/slicedict.py.svg?branch=master)](https://travis-ci.org/looking-for-a-job/slicedict.py/)

### Install
```bash
[sudo] pip install slicedict
```

### Examples
```python
>>> from slicedict import slicedict

>>> medatata = dict(name="pkgname", version="1.0.0", somekey="value")
>>> slicedict(medatata, ["name", "version"])
{'version': '1.0.0', 'name': 'pkgname'}
```

### Sources
+   [`slicedict.slicedict(d, keys)`](https://github.com/looking-for-a-job/slicedict.py/blob/master/__init__.py)