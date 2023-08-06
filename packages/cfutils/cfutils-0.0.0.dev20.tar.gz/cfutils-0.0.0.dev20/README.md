# cfutils

**Chromatogram File Utils**

for sanger sequencing data visualizing, alignment, mutation calling, and trimming etc.

## Demo

![plot chromatogram with mutation](https://raw.githubusercontent.com/yech1990/cfutils/master/data/plot.png)

## How to install?

### form pypi

*(use this way ONLY, if you don't know what't going on)*

```bash
pip install cfutils
```

```bash
$ python
Python 3.6.5 (default, Apr 14 2018, 13:17:30)
[GCC 7.3.1 20180406] on linux

>>>

```

### manipulate the soource code

clone from github

```bash
git clone git@github.com:yech1990/cfutils.git 
```

install dependance

```bash
make init
```

do unittest

```bash
make test
```

## How to use?
 
```python
import cfutils as cf

```

## ChangeLog

- build as python package for pypi
- fix bug that highlihgting wrong base

## TODO

- [ ] call mutation by alignment and plot Chromatogram graphic
- [ ] add a doc
- [x] change xaxis by peak location
