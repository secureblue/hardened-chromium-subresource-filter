%global numjobs %{_smp_build_ncpus}
%global build_target() \
	export NINJA_STATUS="[%2:%f/%t] " ; \
	ninja -j %{numjobs} -C '%1' '%2'
%global chromium_pybin %{__python3}
%global chromebuilddir out/Release

Name:      hardened-chromium-subresource-filter
BuildArch: noarch
Requires:  hardened-chromium
License:   GPL-2.0
Summary:   Subresource filter for hardened-chromium
# This doesn't need to be incremented often
Version:   131.0.6778.69
# Automatically generated version number, so that it doesn't need to be incremented manually
%{lua: print("Release: "..os.time().."\n")}

Source0: chromium-%{version}-clean.tar.xz
Source1: install_filter.sh
Source2: easylist.txt
Source3: easyprivacy.txt
Source4: fanboy-annoyance.txt
Source5: abpindo.txt
Source6: abpvn-IPl6HE.txt
Source7: adblock_bg.txt
Source8: NordicFiltersABP-Inclusion.txt
Source9: easylistchina.txt
Source10: filters.txt
Source11: easylistdutch.txt
Source12: easylistgermany.txt
Source13: EasyListHebrew.txt
Source14: easylistitaly.txt
Source15: easylistlithuania.txt
Source16: easylistpolish.txt
Source17: easylistportuguese.txt
Source18: easylistspanish.txt
Source19: indianlist.txt
Source20: koreanlist.txt
Source21: latvian-list.txt
Source22: liste_ar.txt
Source23: liste_fr.txt
Source24: rolist.txt
Source25: ruadlist.txt
Source26: antiadblockfilters.txt
Source27: SerboCroatianList.txt
Source28: Frellwits-Swedish-Filter.txt
Source29: filter.txt

# Dependencies required
BuildRequires: gn
BuildRequires: ninja-build
BuildRequires: clang
BuildRequires: llvm
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
BuildRequires: pkgconfig(Qt5Core)
BuildRequires: pkgconfig(Qt5Widgets)
BuildRequires: pkgconfig(Qt6Core)
BuildRequires: pkgconfig(Qt6Widgets)
BuildRequires: libva-devel
BuildRequires: libatomic

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
cp %{SOURCE2} .
cp %{SOURCE3} .
cp %{SOURCE4} .
cp %{SOURCE5} .
cp %{SOURCE6} .
cp %{SOURCE7} .
cp %{SOURCE8} .
cp %{SOURCE9} .
cp %{SOURCE10} .
cp %{SOURCE11} .
cp %{SOURCE12} .
cp %{SOURCE13} .
cp %{SOURCE14} .
cp %{SOURCE15} .
cp %{SOURCE16} .
cp %{SOURCE17} .
cp %{SOURCE18} .
cp %{SOURCE19} .
cp %{SOURCE20} .
cp %{SOURCE21} .
cp %{SOURCE22} .
cp %{SOURCE23} .
cp %{SOURCE24} .
cp %{SOURCE25} .
cp %{SOURCE26} .
cp %{SOURCE27} .
cp %{SOURCE28} .
cp %{SOURCE29} .

./%{chromebuilddir}/ruleset_converter --input_format=filter-list --output_format=unindexed-ruleset --input_files=easylist.txt,easyprivacy.txt,fanboy-annoyance.txt,abpindo.txt,abpvn-IPl6HE.txt,adblock_bg.txt,NordicFiltersABP-Inclusion.txt,easylistchina.txt,filters.txt,easylistdutch.txt,easylistgermany.txt,EasyListHebrew.txt,easylistitaly.txt,easylistlithuania.txt,easylistpolish.txt,easylistportuguese.txt,easylistspanish.txt,indianlist.txt,koreanlist.txt,latvian-list.txt,liste_ar.txt,liste_fr.txt,rolist.txt,ruadlist.txt,antiadblockfilters.txt,SerboCroatianList.txt,Frellwits-Swedish-Filter.txt,filter.txt --output_file=hardened-chromium-blocklist > /dev/null
cp hardened-chromium-blocklist ../

# Cleanup
rm -r %{chromebuilddir}

%install
INSTALL_DIR="%{buildroot}%{_sysconfdir}/chromium/filter"
SCRIPT_DIR="%{buildroot}%{_libdir}/chromium-browser/"
mkdir -p "$INSTALL_DIR"
mkdir -p "$SCRIPT_DIR"
install -m 0644 hardened-chromium-blocklist "$INSTALL_DIR/hardened-chromium-blocklist"
install -m 0755 %{SOURCE1} "$SCRIPT_DIR/install_filter.sh"
echo "%{release}" > $INSTALL_DIR/hardened-chromium-blocklist-version.txt
chmod a+r $INSTALL_DIR/hardened-chromium-blocklist-version.txt

%files
%{_sysconfdir}/chromium/filter/hardened-chromium-blocklist
%{_sysconfdir}/chromium/filter/hardened-chromium-blocklist-version.txt
%{_libdir}/chromium-browser/install_filter.sh
