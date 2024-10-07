#! /bin/bash -x

# Preset variables
readonly VERSION="129.0.6668.89" # update this every now-and-again
readonly LIST_SOURCES="https://easylist.to/easylist/easylist.txt https://easylist.to/easylist/easyprivacy.txt"
readonly NAME="hardened-chromium-subresource-filter"
readonly GIT_URL="https://github.com/secureblue/$NAME.git"

# Clone the repo with the spec file and chrowmium source downloader
git clone $GIT_URL
cp $NAME/$NAME.spec ./
cp $NAME/chromium-latest.py ./
python3 ./chromium-latest.py --version $VERSION --stable --cleansources
rm chromium-$VERSION.tar.xz
rm -rf ./chromium-$VERSION
rm -rf ./$NAME

# Get the filters that will be added
wget $LIST_SOURCES
