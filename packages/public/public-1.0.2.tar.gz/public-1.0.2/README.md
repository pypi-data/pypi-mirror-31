[![](https://img.shields.io/pypi/pyversions/public.svg?maxAge=86400)](https://pypi.org/pypi/public/)
[![](https://img.shields.io/pypi/v/public.svg?maxAge=86400)](https://pypi.org/pypi/public/)
[![](https://img.shields.io/badge/libraries.io-public-green.svg)](https://libraries.io/pypi/public)

[![CodeFactor](https://www.codefactor.io/repository/github/looking-for-a-job/public.py/badge)](https://www.codefactor.io/repository/github/looking-for-a-job/public.py)
[![CodeClimate](https://codeclimate.com/github/looking-for-a-job/public.py/badges/gpa.svg)](https://codeclimate.com/github/looking-for-a-job/public.py)
[![Scrutinizer](https://scrutinizer-ci.com/g/looking-for-a-job/public.py/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/looking-for-a-job/public.py/)
[![BetterCodeHub](https://bettercodehub.com/edge/badge/looking-for-a-job/public.py?branch=master)](https://bettercodehub.com/results/looking-for-a-job/public.py)
[![Sonarcloud](https://sonarcloud.io/api/project_badges/measure?project=public.py&metric=code_smells)](https://sonarcloud.io/dashboard?id=public.py)

[![Codecov](https://codecov.io/gh/looking-for-a-job/public.py/branch/master/graph/badge.svg)](https://codecov.io/gh/looking-for-a-job/public.py)
[![CircleCI](https://circleci.com/gh/looking-for-a-job/public.py/tree/master.svg?style=svg)](https://circleci.com/gh/looking-for-a-job/public.py/tree/master)
[![Scrutinizer](https://scrutinizer-ci.com/g/looking-for-a-job/public.py/badges/build.png?b=master)](https://scrutinizer-ci.com/g/looking-for-a-job/public.py/)
[![Semaphore CI](https://semaphoreci.com/api/v1/looking-for-a-job/public-py/branches/master/shields_badge.svg)](https://semaphoreci.com/looking-for-a-job/public-py)
[![Travis](https://api.travis-ci.org/looking-for-a-job/public.py.svg?branch=master)](https://travis-ci.org/looking-for-a-job/public.py/)

### Install
```bash
[sudo] pip install public
```

### Usage
```python
>>> from public import public

>>> @public # decorator

>>> public(*objects) # function
```

### Examples
```python
>>> @public
	def func(): pass

>>> @public
	class CLS: pass

>>> print(__all__)
['CLS',func']

# public(*objects) function
>>> public("name")
>>> public("name1","name2")

>>> print(__all__)
['name','name1','name2']
```

### Sources
+   [`public.public(*objects)`](https://github.com/looking-for-a-job/public.py/blob/master/public/__init__.py)