#! /bin/bash -x

wget https://versionhistory.googleapis.com/v1/chrome/platforms/linux/channels/stable/versions/all/releases?filter=endtime=none -O chromium-version.json
cat chromium-version.json | grep \"version\" | grep -oh "[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*" > chromium-version.txt

# Preset variables
readonly LIST_SOURCES=(
    "https://easylist.to/easylist/easylist.txt"
    "https://easylist.to/easylist/easyprivacy.txt"
    "https://secure.fanboy.co.nz/fanboy-annoyance.txt"
    "https://raw.githubusercontent.com/heradhis/indonesianadblockrules/master/subscriptions/abpindo.txt"
    "https://abpvn.com/filter/abpvn-IPl6HE.txt"
    "https://stanev.org/abp/adblock_bg.txt"
    "https://raw.githubusercontent.com/DandelionSprout/adfilt/master/NorwegianExperimentalList%20alternate%20versions/NordicFiltersABP-Inclusion.txt"
    "https://easylist-downloads.adblockplus.org/easylistchina.txt"
    "https://raw.githubusercontent.com/tomasko126/easylistczechandslovak/master/filters.txt"
    "https://easylist-downloads.adblockplus.org/easylistdutch.txt"
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
readonly NAME="hardened-chromium-subresource-filter"

# Clone the repo with the spec file and chrowmium source downloader
cp $NAME/$NAME.spec ./
cp $NAME/install_filter.sh ./
cp $NAME/chromium-latest.py ./
cp /usr/src/chromium/chromium-*-clean.tar.xz ./
rm -rf ./$NAME

# Get the filters that will be added
counter=0
for url in "${LIST_SOURCES[@]}"; do
    wget "$url" -O filter-$counter.txt
done
