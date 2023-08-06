## Setup
Install dependencies for distribution
```
pipenv install
```

## Creating distribution packages
To generate a source distribution, simply run
```
pipenv run python setup.py sdist
```

To generate a pre-built package with wheel use
```
pipenv run python setup.py bdist_wheel
```

## Uploading Package to testPyPI
To upload the packages in `./dist` to the test python distribution site, you'll need to create an account at [test.pypi.org](https://test.pypi.org/account/register/).

Then you can execute
```
pipenv run twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```
