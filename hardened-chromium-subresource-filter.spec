%global numjobs %{_smp_build_ncpus}
%global build_target() \
	export NINJA_STATUS="[%2:%f/%t] " ; \
	ninja -j %{numjobs} -C '%1' '%2'
%global chromium_pybin %{__python3}
%global chromebuilddir out/Release

# !!! UNDER CONSTRUCTION, WATCH YOUR STEP !!!
Name:      hardened-chromium-subresource-filter
BuildArch: noarch
Requires:  hardened-chromium
License:   GPL-2.0
Summary:   Subresource filter for hardened-chromium
# This doesn't need to be incremented often
Version:   129.0.6668.89
# Automatically generated version number, so that it doesn't need to be incremented manually
%{lua: print("Release: "..os.time().."\n")}

Source0: depot_tools.zip
Source1: chromium-%{version}.tar.xz
Source2: easylist.txt
Source3: easyprivacy.txt

BuildRequires: python3
BuildRequires: git

%description
Filters used by hardened-chromium to provide adblocking.

%build
# Get depot tools needed to build the thing
unzip %{SOURCE0}
ls -l
DEPOT_PATH="$(pwd)/depot_tools"
export PATH="$PATH:$DEPOT_PATH"
echo $PATH
# Get chromium's source
tar -xf %{SOURCE1}
cd chromium-%{version}
mkdir -p %{chromebuilddir}
# Build the converter tool
gn --script-executable=%{chromium_pybin} gen %{chromebuilddir}
%build_target %{chromebuilddir} subresource_filter_tools
cd ../
# Run the tool to generate the blocklist
./chromium-%{version}/out/Release/ruleset_converter --input_format=filter-list --output_format=unindexed-ruleset --input_files=%{SOURCE2},%{SOURCE3} --output_file=hardened-chromium-blocklist

%install
INSTALL_DIR="%{buildroot}%{_sysconfdir}/chromium"
mkdir -p "$INSTALL_DIR"
install -m 0644 hardened-chromium-blocklist "$INSTALL_DIR/hardened-chromium-blocklist"

%post
if [ -d "/home/" ]; then
	cd /home && USERS=*
	INSTALL_DIR="%{_sysconfdir}/chromium"
	for USER in $USERS; do
		OLD_DIR="/home/$USER/.config/chromium"
		echo "Checking for '$OLD_DIR'"
		if [ -d "$OLD_DIR" ]; then
			if [ -d "$OLD_DIR/Subresource Filter" ]; then
				echo "Removing '$OLD_DIR/Subresource Filter'"
				rm -r "$OLD_DIR/Subresource Filter"
			fi
			NEW_DIR="$OLD_DIR/Subresource Filter/Unindexed Rules/%{release}.%{version}"
			echo "Creating '$NEW_DIR'"
			mkdir -p "$NEW_DIR"
			echo "Adding filter list from '$INSTALL_DIR'"
			cp "$INSTALL_DIR/hardened-chromium-blocklist" "$NEW_DIR/Filtering Rules"
			echo "Creating 'manifest.json'"
			cat << EOF > "$NEW_DIR/manifest.json"
{
  "manifest_version": 2,
  "name": "Subresource Filtering Rules",
  "ruleset_format": 1,
  "version": "%{release}.%{version}"
}
EOF
			chown -R $USER "$OLD_DIR"
		fi
	done
fi
echo "Done"

%preun
if [ -d "/home/" ]; then
	cd /home && USERS=*
	for USER in $USERS; do
		DIR="/home/$USER/.config/chromium/Subresource Filter"
		echo "Checking for '$DIR'"
		if [ -d "$DIR" ] && [ $1 -lt 2 ]; then
			echo "Clearing: '$DIR'"
			rm -rf "$DIR"
		fi
	done
fi

%files
%{_sysconfdir}/chromium/hardened-chromium-blocklist
