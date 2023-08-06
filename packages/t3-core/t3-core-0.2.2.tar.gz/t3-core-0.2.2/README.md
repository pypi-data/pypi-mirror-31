# T3 Python Core Library

<a href="https://gitlab.t-3.com/sunoco/t3-python-core/commits/master"><img alt="pipeline status" src="https://gitlab.t-3.com/sunoco/t3-python-core/badges/master/pipeline.svg" /></a>  <a href="https://gitlab.t-3.com/sunoco/t3-python-core/commits/master"><img alt="coverage report" src="https://gitlab.t-3.com/sunoco/t3-python-core/badges/master/coverage.svg" /></a>

## Install

### Setup Virtualenv (optional)
```sh
python -m venv .venv
source .venv/bin/activate
```

### Install
```sh
# Install from pypi
pip install t3-core

# Install in the `src` dir of your python environment
pip install -e git+ssh://git@gitlab.t-3.com/sunoco/t3-python-core.git

# Choose where the clone lives
git clone ssh://git@gitlab.t-3.com/sunoco/t3-python-core.git
pip install -e ./t3-python-core
```

## Testing & Linting
### Test & Coverage Report
```sh
pytest
```

### Lint
```sh
pylama
```
