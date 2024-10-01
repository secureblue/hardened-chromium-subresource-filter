#! /bin/bash -x

# Get chromium's source
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
export PATH="$(pwd)/depot_tools:$PATH"
mkdir ./chromium && cd ./chromium
fetch --nohooks --no-history chromium
cd src
gclient runhooks
gn gen out/Release

# Build the filter generation tool
ninja -C out/Release/ subresource_filter_tools

# Compress the converter and needed libs
cd out/Release
tar cJvf ruleset_converter.tar.xz *.so ruleset_converter
cp ruleset_converter.tar.xz ../../../../

# Cleanup
cd ../../../../
rm -rf ./chromium ./depot_tools

# Print hash to update in the copr script
./get_checksums.sh
