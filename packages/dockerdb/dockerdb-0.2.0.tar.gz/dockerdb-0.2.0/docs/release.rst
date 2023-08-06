How to release
==============

bumpversion

rm -rf dist
python setup.py sdist
git push TAG
twine upload dist/*
