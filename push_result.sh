#!/bin/bash

# bash options
set -o errexit
set -o nounset
set -o pipefail

# for debugging
#set -o xtrace
# Change to data folder
cd ~/public_html/

# Push new result to github
git checkout results

# create new index.html from last result for github.io
ln -f $(ls -trh *xz.html | tail -1) index.html

git commit --message "New result" --quiet index.html
git checkout main
git push --quiet origin results
