#!/bin/bash

# This script will build firefox from source without the webdriver flag to prevent websites from checking that flag

latest_version=$(cat .github/firefox-version.txt)

# Download the source code
curl -LO "https://archive.mozilla.org/pub/firefox/releases/$latest_version/source/firefox-$latest_version.source.tar.xz"
# Extract the source code
tar -xf "firefox-$latest_version.source.tar.xz"

cd firefox-*/

# Remove webdriver flag
sed -i '0,/Navigator includes NavigatorAutomationInformation;/s///' dom/webidl/Navigator.webidl

# build firefox
./mach build

# make directory for release
mkdir -p ../release

# install into release directory
DESTDIR="../release" ./mach install
