#! /bin/bash -x

# Preset variables
readonly GIT_URL="https://github.com/secureblue/hardened-chromium-subresource-filter.git"
readonly LIST_SOURCES="https://easylist.to/easylist/easylist.txt https://easylist.to/easylist/easyprivacy.txt"

# Get chromium's source and depot tools
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
export PATH="$(pwd)/depot_tools:$PATH"
mkdir ./chromium && cd ./chromium
fetch --nohooks --no-history chromium
cd src
gclient runhooks
gn gen out/Release
cd ../../

# Compress for later use
zip -r chromium.zip chromium
zip -r depot_tools.zip depot_tools

# Get the filters that will be added
wget $LIST_SOURCES

# Clone the repo with spec file
git clone $GIT_URL
