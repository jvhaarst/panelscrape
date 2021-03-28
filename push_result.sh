#!/bin/bash

# bash options
set -o errexit
set -o nounset
set -o pipefail

# for debugging
#set -o xtrace

# Push new result to github
git checkout results

# create new index.html from last result for github.io
ln -f $(ls -trh *xz.html | tail -1) index.html

git add index.html
git commit -m "New result" index.html
git checkout main
git push origin results