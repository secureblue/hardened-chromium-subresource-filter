#! /bin/bash

# Copyright 2025 The Trivalent Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

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
