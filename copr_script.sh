#! /bin/bash -x

# Preset variables
readonly CHROMIUM_VERSION="129.0.6668.89" # update this every now-and-again
readonly CHROMIUM_TAR="chromium-$CHROMIUM_VERSION.tar.xz"
readonly CHROMIUM_SOURCE_URL="https://commondatastorage.googleapis.com/chromium-browser-official/$CHROMIUM_TAR"
readonly LIST_SOURCES="https://easylist.to/easylist/easylist.txt https://easylist.to/easylist/easyprivacy.txt"
readonly NAME="hardened-chromium-subresource-filter"
readonly GIT_URL="https://github.com/secureblue/$NAME.git"

# Clone the repo with the spec file and chrowmium source downloader
git clone $GIT_URL
cp $NAME/$NAME.spec ./
cp $NAME/chromium-latest.py ./
python3 ./chromium-latest.py --version $CHROMIUM_VERSION --stable --ffmpegclean --ffmpegarm --cleansources

# Get the filters that will be added
wget $LIST_SOURCES
