#!/bin/bash

# exit when any command fails
set -e

# This script will build firefox from source without the webdriver flag to prevent websites from checking that flag

latest_version=$(cat .github/firefox-version.txt)

# clone the mozilla repo
git clone --depth 1 --branch --single-branch https://github.com/mozilla/gecko-dev.git mozilla-unified

cd mozilla-unified
# switch to the latest stable version branch
# hg update $latest_version

# Remove webdriver flag from the beginning of the file
sed -i '0,/Navigator includes NavigatorAutomationInformation;/s///' dom/webidl/Navigator.webidl
# remove the webdriver boolean code
sed -i '/\/\/ https:\/\/w3c\.github\.io\/webdriver\/webdriver-spec\.html#interface/,/};/d' dom/webidl/Navigator.webidl

# bootstrap the build environment
# Use non-artifact build
yes | ./mach bootstrap --application-choice="Firefox for Desktop"

# build firefox
./mach build

# make directory for release
mkdir -p ../release

# install into release directory
DESTDIR="../release" ./mach install
