#! /bin/bash

# Some variables
readonly INSTALL_DIR="/etc/chromium/filter"
readonly OLD_DIR="$HOME/.config/chromium"
readonly FILTER_VER="$(cat $INSTALL_DIR/filter/hardened-chromium-blocklist-version.txt)"
readonly CURRENT_VER="$(ls $OLD_DIR/Subresource\ Filter/Unindexed\ Rules)"

echo "Checking version" # Debug statement
echo "  Installed version: $CURRENT_VER" # Debug statement
echo "  Package version: $FILTER_VER" # Debug statement
if [ "$FILTER_VER" == "$CURRENT_VER" ]; then
  echo "No need to update, versions match" # Debug statement
  exit 0
fi

readonly NEW_DIR="$OLD_DIR/Subresource Filter/Unindexed Rules/$FILTER_VER"

echo "Removing '$OLD_DIR/Subresource Filter'" # Debug statement
rm -r "$OLD_DIR/Subresource Filter"
echo "Creating '$NEW_DIR'" # Debug statement
mkdir -p "$NEW_DIR"
echo "Adding filter list from '$INSTALL_DIR'" # Debug statement
cp "$INSTALL_DIR/hardened-chromium-blocklist" "$NEW_DIR/Filtering Rules"
echo "Creating 'manifest.json'"
cat << EOF > "$NEW_DIR/manifest.json"
{
  "manifest_version": 2,
  "name": "Subresource Filtering Rules",
  "ruleset_format": 1,
  "version": "$FILTER_VER"
}
EOF
