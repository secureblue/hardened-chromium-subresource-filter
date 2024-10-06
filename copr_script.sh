#! /bin/bash -x

# Preset variables
readonly CHROMIUM_VERSION="129.0.6668.89" # update this every now-and-again
readonly CHROMIUM_TAR="chromium-$CHROMIUM_VERSION.tar.xz"
readonly CHROMIUM_SOURCE_URL="https://commondatastorage.googleapis.com/chromium-browser-official/$CHROMIUM_TAR"
readonly LIST_SOURCES="https://easylist.to/easylist/easylist.txt https://easylist.to/easylist/easyprivacy.txt"
readonly NAME="hardened-chromium-subresource-filter"
readonly GIT_URL="https://github.com/secureblue/$NAME.git"

# Get chromium's source and depot tools
#git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
#zip -r -q depot_tools.zip depot_tools
wget $CHROMIUM_SOURCE_URL $CHROMIUM_SOURCE_URL.hashes
cat $CHROMIUM_TAR.hashes | grep "$(sha384sum $CHROMIUM_TAR)"
if [ "$?" == 1 ]; then
	echo "ERROR! Checksum for $CHROMIUM_TAR doesn't match!"
	exit 1
else
	echo "Checksum for $CHROMIUM_TAR verified."
fi

# Get the filters that will be added
wget $LIST_SOURCES

# Clone the repo with spec file
git clone $GIT_URL
cp $NAME/$NAME.spec ./
