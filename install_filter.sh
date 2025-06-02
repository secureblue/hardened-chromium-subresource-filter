#! /bin/bash

# Some variables
readonly INSTALL_DIR="/etc/trivalent/filter"
readonly OLD_DIR="$HOME/.config/trivalent"
readonly FILTER_VER="$(cat $INSTALL_DIR/trivalent-blocklist-version.txt)"
readonly CURRENT_VER="$(ls $OLD_DIR/Subresource\ Filter/Unindexed\ Rules)"

echo "Checking Subresource Filter version..."
echo "  Installed version: $CURRENT_VER"
echo "  Package version: $FILTER_VER"
if [ "$FILTER_VER" == "$CURRENT_VER" ]; then
  echo "No need to update, versions match"
  exit 0
fi
echo "Version mismatch, updating filter..."

readonly NEW_DIR="$OLD_DIR/Subresource Filter/Unindexed Rules/$FILTER_VER"

echo "Removing '$OLD_DIR/Subresource Filter'"
rm -r "$OLD_DIR/Subresource Filter"
echo "Creating '$NEW_DIR'"
mkdir -p "$NEW_DIR"
echo "Adding filter list from '$INSTALL_DIR'"
cp "$INSTALL_DIR/trivalent-blocklist" "$NEW_DIR/Filtering Rules"
echo "Creating 'manifest.json'"
cat << EOF > "$NEW_DIR/manifest.json"
{
  "manifest_version": 2,
  "name": "Subresource Filtering Rules",
  "ruleset_format": 1,
  "version": "$FILTER_VER"
}
EOF
echo "Subresource Filter successfully updated"
