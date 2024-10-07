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

Source0: chromium-%{version}.tar.xz
Source1: easylist.txt
Source2: easyprivacy.txt

BuildRequires: gn
BuildRequires: ninja-build
BuildRequires: lld
BuildRequires: rustc
BuildRequires: nss-devel >= 3.26
BuildRequires: glib2-devel
BuildRequires: %{chromium_pybin}
BuildRequires: cups-devel
BuildRequires: libxkbcommon-devel
BuildRequires: libudev-devel
BuildRequires: dbus-devel
BuildRequires: libdrm-devel
BuildRequires: atk-devel
BuildRequires: libcurl-devel
BuildRequires: at-spi2-atk-devel
BuildRequires: pango-devel
BuildRequires: mesa-libgbm-devel
BuildRequires: gtk3-devel
BuildRequires: mesa-libGL-devel
# One of the python scripts invokes git to look for a hash. So helpful.
BuildRequires: /usr/bin/git


%description
Filter used by hardened-chromium to provide content blocking.


%prep

%setup -q -n chromium-%{version}


%build

FLAGS=' -Wno-deprecated-declarations -Wno-unknown-warning-option -Wno-unused-command-line-argument'
FLAGS+=' -Wno-unused-but-set-variable -Wno-unused-result -Wno-unused-function -Wno-unused-variable'
FLAGS+=' -Wno-unused-const-variable -Wno-unneeded-internal-declaration -Wno-unknown-attributes -Wno-unknown-pragmas'

CFLAGS="$FLAGS"
CXXFLAGS="$FLAGS"
LDFLAGS="-Wl,-z,now -Wl,-z,pack-relative-relocs"

export CC=clang
export CXX=clang++
export AR=llvm-ar
export NM=llvm-nm
export READELF=llvm-readelf
export CFLAGS
export CXXFLAGS
export LDFLAGS

export RUSTC_BOOTSTRAP=1
rustc_version="$(rustc --version)"
rust_bindgen_root="%{_prefix}"

# set clang version
clang_version="20"
clang_base_path="$(pwd)/third_party/llvm-build/Release+Asserts/"

CHROMIUM_GN_DEFINES=""
CHROMIUM_GN_DEFINES+=' custom_toolchain="//build/toolchain/linux/unbundle:default"'
CHROMIUM_GN_DEFINES+=' host_toolchain="//build/toolchain/linux/unbundle:default"'
CHROMIUM_GN_DEFINES+=' system_libdir="%{_lib}"'
CHROMIUM_GN_DEFINES+=' is_clang=true'
CHROMIUM_GN_DEFINES+=" clang_base_path=\"$clang_base_path\""
CHROMIUM_GN_DEFINES+=" clang_version=\"$clang_version\""
CHROMIUM_GN_DEFINES+=' clang_use_chrome_plugins=false'
CHROMIUM_GN_DEFINES+=' use_lld=true'
CHROMIUM_GN_DEFINES+=' rust_sysroot_absolute="%{_prefix}"'
CHROMIUM_GN_DEFINES+=" rust_bindgen_root=\"$rust_bindgen_root\""
CHROMIUM_GN_DEFINES+=" rustc_version=\"$rustc_version\""
CHROMIUM_GN_DEFINES+=' use_sysroot=false'
CHROMIUM_GN_DEFINES+=' chrome_pgo_phase=0'
export CHROMIUM_GN_DEFINES

mkdir -p %{chromebuilddir} && cp -a %{_bindir}/gn %{chromebuilddir}/

# Build the converter tool
%{chromebuilddir}/gn --script-executable=%{chromium_pybin} gen --args="$CHROMIUM_GN_DEFINES" %{chromebuilddir}
%build_target %{chromebuilddir} subresource_filter_tools

# Run the tool to generate the blocklist
cp %{SOURCE1} .
cp %{SOURCE2} .
./%{chromebuilddir}/ruleset_converter --input_format=filter-list --output_format=unindexed-ruleset --input_files=easylist.txt,easyprivacy.txt --output_file=hardened-chromium-blocklist > /dev/null
cp hardened-chromium-blocklist ../

# Cleanup
rm -r %{chromebuilddir}


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
