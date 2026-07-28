#! /bin/bash -x

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

set -ueo pipefail

# Preset variables
declare -r LIST_SOURCES=(
    "https://easylist.to/easylist/easylist.txt"
    "https://easylist.to/easylist/easyprivacy.txt"
    "https://secure.fanboy.co.nz/fanboy-annoyance.txt"
    "https://raw.githubusercontent.com/heradhis/indonesianadblockrules/master/subscriptions/abpindo.txt"
    "https://abpvn.com/filter/abpvn-IPl6HE.txt"
    "https://stanev.org/abp/adblock_bg.txt"
    "https://raw.githubusercontent.com/DandelionSprout/adfilt/master/NorwegianExperimentalList%20alternate%20versions/NordicFiltersABP-Inclusion.txt"
    "https://easylist-downloads.adblockplus.org/easylistchina.txt"
    "https://raw.githubusercontent.com/tomasko126/easylistczechandslovak/master/filters.txt"
    "https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_8_Dutch/filter.txt"
    "https://easylist.to/easylistgermany/easylistgermany.txt"
    "https://raw.githubusercontent.com/easylist/EasyListHebrew/master/EasyListHebrew.txt"
    "https://easylist-downloads.adblockplus.org/easylistitaly.txt"
    "https://raw.githubusercontent.com/EasyList-Lithuania/easylist_lithuania/master/easylistlithuania.txt"
    "https://easylist-downloads.adblockplus.org/easylistpolish.txt"
    "https://easylist-downloads.adblockplus.org/easylistportuguese.txt"
    "https://easylist-downloads.adblockplus.org/easylistspanish.txt"
    "https://easylist-downloads.adblockplus.org/indianlist.txt"
    "https://easylist-downloads.adblockplus.org/koreanlist.txt"
    "https://raw.githubusercontent.com/Latvian-List/adblock-latvian/master/lists/latvian-list.txt"
    "https://easylist-downloads.adblockplus.org/liste_ar.txt"
    "https://easylist-downloads.adblockplus.org/liste_fr.txt"
    "https://zoso.ro/pages/rolist.txt"
    "https://easylist-downloads.adblockplus.org/ruadlist.txt"
    "https://easylist-downloads.adblockplus.org/antiadblockfilters.txt"
    "https://raw.githubusercontent.com/DandelionSprout/adfilt/refs/heads/master/SerboCroatianList.txt"
    "https://raw.githubusercontent.com/lassekongo83/Frellwits-filter-lists/master/Frellwits-Swedish-Filter.txt"
    "https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_7_Japanese/filter.txt"
)
declare -r NAME="trivalent-subresource-filter"

# Clone the repo with the spec file and chromium source downloader
cp "$NAME/$NAME.spec" ./
cp "$NAME/use-cwd-for-gclient-path.patch" ./
cp "$NAME/150-remove-sysroot-dep.patch" ./
cp "$NAME/install_filter.sh" ./
cp /usr/src/chromium/chromium-*-clean.tar.xz ./
cp /usr/src/chromium/chromium-version.txt ./
rm -rf "./$NAME"

# Get the filters that will be added
declare -i counter=1
for url in "${LIST_SOURCES[@]}"; do
    wget "$url" -O "filter-$counter.txt"
    counter=$((counter+1))
done

# Generate changelog from 50 most recent successful Copr builds
curl -fLsS --retry 3 "https://copr.fedorainfracloud.org/api_3/build/list?ownername=secureblue&projectname=packages&packagename=${NAME}&status=succeeded" \
    | jq -cr '.items[0:50][] | "* \(.submitted_on | strftime("%a %b %d %Y")) secureblue <noreply@secureblue.dev> - \(.source_package.version)"' \
    >> "${NAME}.spec"
