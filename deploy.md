# Deploying to PyPi

- [Twine - publishing utility for PyPi](https://twine.readthedocs.io/en/latest/)

```

1. Install it via pip install twine
2. Make sure your .pypirc file has the correct credentials for test.pypi.org because that is a separate database from production pypi.
3. Build your sdist python setup.py sdist.
4. Use twine upload --repository pypitest dist/* for your test upload.
5. Use twine upload --repository pypi dist/* for your production upload.

```

- [PyPirc - configurations for deploying to distutil servers](https://packaging.python.org/specifications/pypirc/)


## References

- host python packages using dithub on pypi|https://www.codementor.io/@arpitbhayani/host-your-python-package-using-github-on-pypi-du107t7ku
- publish to pypi|https://realpython.com/pypi-publish-python-package/
