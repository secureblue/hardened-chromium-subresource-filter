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
Source1: depot_tools.zip
Source2: easylist.txt
Source3: easyprivacy.txt

# Copy pasted from hardened-chromium.spec because yes
BuildRequires: golang-github-evanw-esbuild
BuildRequires: clang
BuildRequires: clang-tools-extra
BuildRequires: llvm
BuildRequires: lld
BuildRequires: rustc
BuildRequires: bindgen-cli
BuildRequires: libzstd-devel
BuildRequires: pkgconfig(libavcodec)
BuildRequires: pkgconfig(libavfilter)
BuildRequires: pkgconfig(libavformat)
BuildRequires: pkgconfig(libavutil)
Conflicts: libavformat-free%{_isa} < 6.0.1
Conflicts: ffmpeg-libs%{_isa} < 6.0.1-2
BuildRequires: pkgconfig(openh264)
BuildRequires:	alsa-lib-devel
BuildRequires:	atk-devel
BuildRequires:	bison
BuildRequires:	cups-devel
BuildRequires:	dbus-devel
BuildRequires:	desktop-file-utils
BuildRequires:	expat-devel
BuildRequires:	flex
BuildRequires:	fontconfig-devel
BuildRequires:	glib2-devel
BuildRequires:	glibc-devel
BuildRequires:	gperf
BuildRequires: pkgconfig(Qt5Core)
BuildRequires: pkgconfig(Qt5Widgets)
BuildRequires: pkgconfig(Qt6Core)
BuildRequires: pkgconfig(Qt6Widgets)
BuildRequires: compiler-rt
BuildRequires:	harfbuzz-devel >= 2.4.0
BuildRequires: libatomic
BuildRequires:	libcap-devel
BuildRequires:	libcurl-devel
BuildRequires:	libdrm-devel
BuildRequires:	libgcrypt-devel
BuildRequires:	libudev-devel
BuildRequires:	libuuid-devel
BuildRequires:	libusb-compat-0.1-devel
BuildRequires:	libutempter-devel
BuildRequires:	libXdamage-devel
BuildRequires:	libXtst-devel
BuildRequires:	xcb-proto
BuildRequires:	mesa-libgbm-devel
BuildRequires: nodejs
BuildRequires: gn
BuildRequires:	nss-devel >= 3.26
BuildRequires:	pciutils-devel
BuildRequires:	pulseaudio-libs-devel
BuildRequires:	pipewire-devel
BuildRequires: libappstream-glib

# Fedora tries to use system libs whenever it can.
BuildRequires:	bzip2-devel
BuildRequires:	dbus-glib-devel
# For eu-strip
BuildRequires:	elfutils
BuildRequires:	elfutils-libelf-devel
BuildRequires:	flac-devel
BuildRequires:	freetype-devel
BuildRequires: google-crc32c-devel
BuildRequires: libdav1d-devel
BuildRequires: highway-devel
BuildRequires: libsecret-devel
BuildRequires: double-conversion-devel
BuildRequires: libXNVCtrl-devel
# One of the python scripts invokes git to look for a hash. So helpful.
BuildRequires:	/usr/bin/git
BuildRequires:	hwdata
BuildRequires:	kernel-headers
BuildRequires:	libevent-devel
BuildRequires:	libffi-devel
BuildRequires:	libjpeg-devel
BuildRequires:	libpng-devel
BuildRequires: openjpeg2-devel
BuildRequires: lcms2-devel
BuildRequires: libtiff-devel
BuildRequires:	libudev-devel
Requires: libusbx >= 1.0.21-0.1.git448584a
BuildRequires: libusbx-devel >= 1.0.21-0.1.git448584a
BuildRequires:	libva-devel
BuildRequires:	libwebp-devel
BuildRequires:	libxslt-devel
BuildRequires:	libxshmfence-devel
BuildRequires:	mesa-libGL-devel
BuildRequires:	opus-devel
BuildRequires: %{chromium_pybin}
BuildRequires:	pkgconfig(gtk+-3.0)
BuildRequires: python3-jinja2
BuildRequires: brotli-devel
BuildRequires: speech-dispatcher-devel
BuildRequires: yasm
BuildRequires: zlib-devel
BuildRequires:	systemd
BuildRequires: ninja-build
BuildRequires: libevdev-devel

%description
Filters used by hardened-chromium to provide adblocking.

%build
# Get chromium's source
#%setup -q -n chromium-%{version}
tar -xf %{SOURCE1}
cd chromium-%{version}
mkdir -p %{chromebuilddir}

# Get depot tools needed to build the thing
unzip %{SOURCE1}
DEPOT_PATH="$(pwd)/depot_tools"
export PATH="$PATH:$DEPOT_PATH"

export CC=clang
export CXX=clang++
export AR=llvm-ar
export NM=llvm-nm
export READELF=llvm-readelf

export RUSTC_BOOTSTRAP=1
rustc_version="$(rustc --version)"
rust_bindgen_root="%{_prefix}"

# set clang version
clang_version="$(clang --version | sed -n 's/clang version //p' | cut -d. -f1)"
clang_base_path="$(clang --version | grep InstalledDir | cut -d' ' -f2 | sed 's#/bin##')"

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

# use system libraries
system_libs=()
system_libs+=(brotli)
system_libs+=(crc32c)
system_libs+=(dav1d)
system_libs+=(highway)
system_libs+=(fontconfig)
system_libs+=(ffmpeg)
system_libs+=(freetype)
system_libs+=(harfbuzz-ng)
system_libs+=(libdrm)
system_libs+=(libevent)
system_libs+=(libjpeg)
system_libs+=(libpng)
system_libs+=(libusb)
system_libs+=(libwebp)
system_libs+=(libxml)
system_libs+=(libxslt)
system_libs+=(opus)
system_libs+=(double-conversion)
system_libs+=(libsecret)
system_libs+=(libXNVCtrl)
system_libs+=(flac)
system_libs+=(zstd)
system_libs+=(openh264)

build/linux/unbundle/replace_gn_files.py --system-libraries ${system_libs[@]}

# Build the converter tool
gn --script-executable=%{chromium_pybin} gen --args="$CHROMIUM_GN_DEFINES" %{chromebuilddir}
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
