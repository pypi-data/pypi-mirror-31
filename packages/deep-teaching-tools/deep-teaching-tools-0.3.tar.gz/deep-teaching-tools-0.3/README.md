# Deep Teaching Tools

This Python module is part of the [deep.TEACHING](http://www.deep-teaching.org) project and provides CLI tools to work
with Jupyter notebooks and teaching materials.

## Installation

Option 1: Install in user's home directory

```bash
pip3 install --user deep-teaching-tools
```

Option 2: Install from source
```bash
git clone https://gitlab.com/deep.TEACHING/deep-teaching-tools.git
pip3 install --user ./deep-teaching-tools/
```

## Usage

```bash
dtt --help
```

## Developer Documentation

Distribute on PyPI:

```bash
# get code
git clone https://gitlab.com/deep.TEACHING/deep-teaching-tools.git
cd deep-teaching-tools
# make code changes and update setup.py
vi setup.py
# create tarball
python3 setup.py sdist
# upload tarball
pip3 install --user twine
twine upload dist/deep-teaching-tools-0.1
```

## License

[MIT](/LICENSE)

## Acknowledgements

The Deep Teaching Commons software is developed at HTW Berlin - University of Applied Sciences.

The work is supported by the German Ministry of Education and Research (BMBF).
