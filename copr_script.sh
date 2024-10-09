#! /bin/bash -x

# Preset variables
readonly VERSION="129.0.6668.100" # update this every now-and-again
readonly LIST_SOURCES="https://easylist.to/easylist/easylist.txt https://easylist.to/easylist/easyprivacy.txt"
readonly NAME="hardened-chromium-subresource-filter"

# Copy the spec file and chromium source downloader from the cloned repo
cp $NAME/$NAME.spec ./
cp $NAME/install_filter.sh ./
cp $NAME/chromium-latest.py ./
python3 ./chromium-latest.py --version $VERSION --stable --cleansources
rm chromium-$VERSION.tar.xz
rm -rf ./chromium-$VERSION

# Get the filters that will be added
wget $LIST_SOURCES
