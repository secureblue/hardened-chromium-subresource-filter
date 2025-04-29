%global numjobs %{_smp_build_ncpus}
%global build_target() \
	export NINJA_STATUS="[%2:%f/%t] " ; \
	ninja -j %{numjobs} -C '%1' '%2'
%global chromium_pybin %{__python3}
%global chromebuilddir out/Release
%global chromium_name trivalent

Source69: chromium-version.txt

Name:      %{chromium_name}-subresource-filter
BuildArch: noarch
Requires:  %{chromium_name}
License:   GPL-2.0
Summary:   Subresource filter for %{chromium_name}
%{lua:
       local f = io.open(macros['_sourcedir']..'/chromium-version.txt', 'r')
       local content = f:read "*all"
       rpm.execute("echo", content)
       -- This will dynamically set the version based on chromium's latest stable release channel
       print("Version: "..content.."\n")

       -- This will automatically increment the release every ~16 minutes
       print("Release: "..(os.time() // 1000).."\n")
}

Source0: chromium-%{version}-clean.tar.xz
Source1: install_filter.sh
%{lua:
    if posix.getenv("HOME") == "/builddir" then
        filters = rpm.glob('/builddir/build/SOURCES/filter-*.txt')
    else
        filters = rpm.glob(macros['_sourcedir']..'/filter-*.txt')
    end
    local count = 1
    for f in ipairs(filters) do
    	local altcount=count+1
        os.execute("echo 'Adding source in "..filters[f].."'")
        printSource = "Source"..altcount..": filter-"..count..".txt"
        rpm.execute("echo", printSource)
        print(printSource.."\n")
        count = count + 1
    end
    rpm.define("_filterCount "..count-1)
}


# set clang_lib path
Patch358: chromium-127-rust-clanglib.patch
Patch359: use-clang19-cflag.patch

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
BuildRequires: rust-bindgen-devel
BuildRequires: bindgen-cli
BuildRequires: clang-devel
BuildRequires: compiler-rt

%description
Filter used by %{chromium_name} to provide content blocking.

%prep
%setup -q -n chromium-%{version}
%patch -P359 -p1 -b .use-clang19-cflag

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
export RUST_BACKTRACE=full
rustc_version="$(rustc --version)"
rust_bindgen_root="%{_prefix}"

# # set clang version
clang_version="$(clang --version | sed -n 's/clang version //p' | cut -d. -f1)"
%if 0%{?fedora} > 41
clang_base_path="$(PATH=/usr/bin:/usr/sbin which clang | sed 's#/bin/.*##')"
%else
clang_base_path="$(clang --version | grep InstalledDir | cut -d' ' -f2 | sed 's#/bin##')"
%endif

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

# copy the filters over and generate the string of said filters
for filter in %{_sourcedir}/filter-*.txt; do
	cp $filter .
done
filters=""
for filter in filter-*.txt; do
	filters="$filters$filter,"
done

# Run the tool to generate the blocklist
./%{chromebuilddir}/ruleset_converter --input_format=filter-list --output_format=unindexed-ruleset --input_files=${filters::-1} --output_file=%{chromium_name}-blocklist > /dev/null
cp %{chromium_name}-blocklist ../

# Cleanup
rm -r %{chromebuilddir}

%install
INSTALL_DIR="%{buildroot}%{_sysconfdir}/%{chromium_name}/filter"
SCRIPT_DIR="%{buildroot}%{_libdir}/%{chromium_name}/"
mkdir -p "$INSTALL_DIR"
mkdir -p "$SCRIPT_DIR"
install -m 0644 %{chromium_name}-blocklist "$INSTALL_DIR/%{chromium_name}-blocklist"
install -m 0755 %{SOURCE1} "$SCRIPT_DIR/install_filter.sh"
echo "%{release}" > $INSTALL_DIR/%{chromium_name}-blocklist-version.txt
chmod a+r $INSTALL_DIR/%{chromium_name}-blocklist-version.txt

%files
%{_sysconfdir}/%{chromium_name}/filter/%{chromium_name}-blocklist
%{_sysconfdir}/%{chromium_name}/filter/%{chromium_name}-blocklist-version.txt
%{_libdir}/%{chromium_name}/install_filter.sh
