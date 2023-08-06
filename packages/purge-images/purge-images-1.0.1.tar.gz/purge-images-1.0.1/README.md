[![](https://img.shields.io/badge/language-Unix%20Shell-blue.svg?maxAge=604800)]()
[![](https://img.shields.io/pypi/v/purge-images.svg?maxAge=86400)](https://pypi.org/pypi/purge-images/)

[![CircleCI](https://circleci.com/gh/looking-for-a-job/purge-images/tree/master.svg?style=svg)](https://circleci.com/gh/looking-for-a-job/purge-images/tree/master)
[![Scrutinizer](https://scrutinizer-ci.com/g/looking-for-a-job/purge-images/badges/build.png?b=master)](https://scrutinizer-ci.com/g/looking-for-a-job/purge-images/)
[![Semaphore CI](https://semaphoreci.com/api/v1/looking-for-a-job/purge-images/branches/master/shields_badge.svg)](https://semaphoreci.com/looking-for-a-job/purge-images)
[![Travis](https://api.travis-ci.org/looking-for-a-job/purge-images.svg?branch=master)](https://travis-ci.org/looking-for-a-job/purge-images/)

### Install
```bash
$ [sudo] pip install purge-images
```

### Features
+   purge html page images (badges)

### Usage
```bash
usage: purge-images url ...
```

### Examples
```bash
url="https://github.com/owner/repo"
purge-images "$url"
```