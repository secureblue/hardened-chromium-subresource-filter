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

set -oue pipefail

declare -ri LOG_LEVEL="${BROWSER_LOG_LEVEL:-0}"

function logecho () {
  if [[ $LOG_LEVEL -gt 1 ]]; then
    echo "$1"
  fi
}

declare -r INSTALL_DIR="/etc/trivalent/filter"
declare -r OLD_DIR="$HOME/.config/trivalent"
declare -r FILTER_VER=$(<"$INSTALL_DIR/trivalent-blocklist-version.txt")
declare -r CURRENT_VER=$(ls "$OLD_DIR/Subresource Filter/Unindexed Rules")

logecho "Checking Subresource Filter version..."
logecho "  Installed version: $CURRENT_VER"
logecho "  Package version: $FILTER_VER"
if [ "$FILTER_VER" == "$CURRENT_VER" ]; then
  logecho "No need to update, versions match"
  exit 0
fi
logecho "Version mismatch, updating subresource filter..."

declare -r NEW_DIR="$OLD_DIR/Subresource Filter/Unindexed Rules/$FILTER_VER"

logecho "Removing '$OLD_DIR/Subresource Filter'"
rm -r "$OLD_DIR/Subresource Filter"
logecho "Creating '$NEW_DIR'"
mkdir -p "$NEW_DIR"
logecho "Adding filter list from '$INSTALL_DIR'"
cp "$INSTALL_DIR/trivalent-blocklist" "$NEW_DIR/Filtering Rules"
logecho "Creating 'manifest.json'"
cat << EOF > "$NEW_DIR/manifest.json"
{
  "manifest_version": 2,
  "name": "Subresource Filtering Rules",
  "ruleset_format": 1,
  "version": "$FILTER_VER"
}
EOF
echo "Subresource Filter successfully updated"
