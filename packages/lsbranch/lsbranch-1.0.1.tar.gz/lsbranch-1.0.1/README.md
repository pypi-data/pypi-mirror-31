<h1>lsbranch</h1>

[![PyPI version](https://badge.fury.io/py/lsbranch.svg)](https://badge.fury.io/py/lsbranch)

<p>List all directories with .git subdirectory and show current branch for each.</p>

<h3>Instalation</h3>

```
pip install lsbranch
```

<h3>CLI Usage</h3>

```bash
Usage: lsbranch [OPTIONS]

  List all directories with .git subdirectory and show current branch for
  each

Options:
  -r, --recursive  Recursive directory search
  -p, --path PATH  Path to search
  --help           Show this message and exit.
```

<p>Let's say that you want to list all git dirs in current dir, recursively</p>


```bash
> lsbranch -r -p .
```

<p>Let's say you just want to list all git dirs in current dir, not recursively</p>


```bash
> lsbranch
```