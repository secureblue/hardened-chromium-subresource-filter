#! /bin/bash -x

# Preset variables
readonly SPEC_FILE="hardened-chromium-subresource-filter.spec"
readonly CONVERTER_FILE="ruleset_converter"
readonly GIT_URL="https://raw.githubusercontent.com/secureblue/hardened-chromium-subresource-filter/refs/heads/master/"

# Checksums use SHA384
readonly SPEC_CHECKSUM="3a75b3b1605e11b8c084775ab92efddcb3e106c441d176ff62c3c4b546b04181ad04a60b1d251b84a101dd9830fc7d9b"
readonly CONVERTER_CHECKSUM="28e225e884b2e657962ddb1b8900c41782e21a5c6208c30f75617d83bdaabc7027f0eaf3be873aa99d5a794d62c72d30"

LISTS="easylist.txt,easyprivacy.txt"
LIST_SOURCES="https://easylist.to/easylist/easylist.txt https://easylist.to/easylist/easyprivacy.txt"

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

download_and_verify $SPEC_FILE $GIT_URL/$SPEC_FILE $SPEC_CHECKSUM
download_and_verify $CONVERTER_FILE.tar.xz $GIT_URL/$CONVERTER_FILE.tar.xz $CONVERTER_CHECKSUM

# Get the filters that will be added
for source in $LIST_SOURCES; do
	wget $source
done

# Run the converter file to generate the filterlist
tar xvf $CONVERTER_FILE.tar.xz
./$CONVERTER_FILE/$CONVERTER_FILE --input_format=filter-list --output_format=unindexed-ruleset --input_files=$LISTS --output_file=hardened-chromium_blocklist

# Cleanup (only needed for a local, non-copr, run)
rm easylist.txt easyprivacy.txt
rm -rf ruleset_converter/
