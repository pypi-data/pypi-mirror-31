# pypi_play

Read the following:
http://python-packaging.readthedocs.io/en/latest/minimal.html
https://packaging.python.org/tutorials/distributing-packages/#install-requires

To work in your own env:
`pip install -e .`

Make an account via https://pypi.org/account/register/
Add a file called `.pyirc` to your $~ (home dir)
Add this to `.pyirc`:
```
[pypi]
username = <username>
password = <password>
```

To package your project:
```
pip install twine
python setup.py sdist
pip install wheel
python setup.py bdist_wheel --universal
twine upload dist/*
```
`twine upload dist/*` doesn't work use `twine upload dist/* --skip-existing`
