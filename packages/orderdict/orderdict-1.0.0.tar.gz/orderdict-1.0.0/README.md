[![](https://img.shields.io/pypi/pyversions/orderdict.svg?maxAge=86400)](https://pypi.org/pypi/orderdict/)
[![](https://img.shields.io/pypi/v/orderdict.svg?maxAge=86400)](https://pypi.org/pypi/orderdict/)
[![](https://img.shields.io/badge/libraries.io-orderdict-green.svg)](https://libraries.io/pypi/orderdict)

[![CodeFactor](https://www.codefactor.io/repository/github/looking-for-a-job/orderdict.py/badge)](https://www.codefactor.io/repository/github/looking-for-a-job/orderdict.py)
[![CodeClimate](https://codeclimate.com/github/looking-for-a-job/orderdict.py/badges/gpa.svg)](https://codeclimate.com/github/looking-for-a-job/orderdict.py)
[![Scrutinizer](https://scrutinizer-ci.com/g/looking-for-a-job/orderdict.py/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/looking-for-a-job/orderdict.py/)
[![BetterCodeHub](https://bettercodehub.com/edge/badge/looking-for-a-job/orderdict.py?branch=master)](https://bettercodehub.com/results/looking-for-a-job/orderdict.py)
[![Sonarcloud](https://sonarcloud.io/api/project_badges/measure?project=orderdict.py&metric=code_smells)](https://sonarcloud.io/dashboard?id=orderdict.py)

[![Codecov](https://codecov.io/gh/looking-for-a-job/orderdict.py/branch/master/graph/badge.svg)](https://codecov.io/gh/looking-for-a-job/orderdict.py)
[![CircleCI](https://circleci.com/gh/looking-for-a-job/orderdict.py/tree/master.svg?style=svg)](https://circleci.com/gh/looking-for-a-job/orderdict.py/tree/master)
[![Scrutinizer](https://scrutinizer-ci.com/g/looking-for-a-job/orderdict.py/badges/build.png?b=master)](https://scrutinizer-ci.com/g/looking-for-a-job/orderdict.py/)
[![Semaphore CI](https://semaphoreci.com/api/v1/looking-for-a-job/orderdict-py/branches/master/shields_badge.svg)](https://semaphoreci.com/looking-for-a-job/orderdict-py)
[![Travis](https://api.travis-ci.org/looking-for-a-job/orderdict.py.svg?branch=master)](https://travis-ci.org/looking-for-a-job/orderdict.py/)

### Install
```bash
[sudo] pip install orderdict
```

### Examples
```python
>>> from orderdict import orderdict

>>> metadata = dict(version="1.0.0", name="pkgname")
{'version': '1.0.0', 'name': 'pkgname'}

>>> orderdict(["name", "version"], metadata)
OrderedDict([('name', 'pkgname'), ('version', '1.0.0')])
```

### Sources
+   [`orderdict.orderdict(ordering, *args, **kwargs)`](https://github.com/looking-for-a-job/orderdict.py/blob/master/__init__.py)