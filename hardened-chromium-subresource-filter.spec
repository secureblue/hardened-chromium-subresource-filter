Name:      hardened-chromium-subresource-filter
BuildArch: noarch
Requires:  hardened-chromium
Source0:   hardened-chromium-blocklist
License:   GPL-2.0
Summary:   Subresource filter for hardened-chromium
Version:   1.0
# Automatically generated version number, so that it doesn't need to be incremented manually
%{lua: print("Release: "..os.time().."\n")}

%description
Filters used by hardened-chromium to provide adblocking.

%install
INSTALL_DIR="%{buildroot}%{_sysconfdir}/chromium"
mkdir -p "$INSTALL_DIR"
install -m 0644 %{SOURCE0} "$INSTALL_DIR/hardened-chromium-blocklist"

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
