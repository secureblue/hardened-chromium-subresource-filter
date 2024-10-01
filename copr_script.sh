#! /bin/bash -x

# Preset variables
readonly SPEC_FILE="hardened-chromium-subresource-filter.spec"
readonly SPEC_SHA384_CHECKSUM="3a75b3b1605e11b8c084775ab92efddcb3e106c441d176ff62c3c4b546b04181ad04a60b1d251b84a101dd9830fc7d9b"
readonly GIT_URL="https://raw.githubusercontent.com/secureblue/hardened-chromium-subresource-filter/refs/heads/"
readonly LIST_SOURCES="https://easylist.to/easylist/easylist.txt https://easylist.to/easylist/easyprivacy.txt"

# Get a file from whatever source and, given a checksum, validate it
download_and_verify() {
	FAILED_COUNT=0
	while [ "$FAILED_COUNT" -lt $((4)) ]; do
		wget $2
		sha384sum $1 | grep -w $3
		if [ "$?" == 1 ]; then
			echo "ERROR! Checksum for $1 does not match!"
			rm $1
			if [ "$FAILED_COUNT" == $((3)) ]; then
				echo "Failed to validate too many times, exiting..."
				exit 1
			else
				echo "Retrying..."
			fi
			FAILED_COUNT=$((FAILED_COUNT+1))
		else
			echo "$1 checksum validated."
			break
		fi
	done
}

download_and_verify $SPEC_FILE $GIT_URL/$SPEC_FILE $SPEC_SHA384_CHECKSUM

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
