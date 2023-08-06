# Not Steov

new version:

    git merge --no-ff $BRANCH # or git commit
    vi VERSION.txt # increment the relevant portion
    git commit -a --amend --no-ed
    git tag -a v$(cat VERSION.txt) -m Version\ $(cat VERSION.txt)
    git push origin master --tags
    rm -rf dist build *.egg-info
    python3 setup.py sdist bdist_wheel
    twine upload dist/*
