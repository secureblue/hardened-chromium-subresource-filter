%global numjobs %{_smp_build_ncpus}
%global chromebuilddir out/Release
%global chromium_name trivalent
%global debug_package %{nil}

Source69: chromium-version.txt

# The system toolchain is more out-of-date compared to chromium's
# It also loses out on some performance optimisations that chromium's toolchain can provide (like siso)
# This is needed for non-x64 arches since the chromium toolchain doesn't support anything but x64
%ifarch x86_64
%global use_system_toolchain 0
%else
%global use_system_toolchain 1
%endif

Name:      %{chromium_name}-subresource-filter
Requires:  %{chromium_name}
License:   Apache-2.0
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


%{lua:
    rpm.execute("pwd")
    if posix.getenv("HOME") == "/builddir" then
        fpatches = rpm.glob('/builddir/build/SOURCES/fedora-*.patch')
    else
        fpatches = rpm.glob(macros['_sourcedir']..'/fedora-*.patch')
    end

    local count = 0
    local printPatch = ""

    if macros['use_system_toolchain'] == "1" then
        count = 1000
        printPatch = ""
        for p in ipairs(fpatches) do
            os.execute("echo 'Patching in "..fpatches[p].."'")
            printPatch = "Patch"..count..": fedora-"..count..".patch"
            rpm.execute("echo", printPatch)
            print(printPatch.."\n")
            count = count + 1
        end
        rpm.define("_fedoraPatchCount "..count-1)
        os.execute("echo 'Autopatch F: "..macros['_fedoraPatchCount'].."'")
    end
}

ExclusiveArch: x86_64 aarch64

# Dependencies required
BuildRequires: nss-devel >= 3.26
BuildRequires: glib2-devel
BuildRequires: %{__python3}
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
BuildRequires: pkgconfig(Qt5Core)
BuildRequires: pkgconfig(Qt5Widgets)
BuildRequires: pkgconfig(Qt6Core)
BuildRequires: pkgconfig(Qt6Widgets)
BuildRequires: libva-devel
BuildRequires: libatomic
# One of the python scripts invokes git to look for a hash. So helpful.
BuildRequires: git-core
%if %{use_system_toolchain}
BuildRequires: clang
BuildRequires: clang-tools-extra
BuildRequires: compiler-rt
BuildRequires: llvm
BuildRequires: lld
BuildRequires: rustc
BuildRequires: bindgen-cli
BuildRequires: ninja-build
BuildRequires: gn
%global build_target() \
	export NINJA_STATUS="[%2:%f/%t] " ; \
	ninja -j %{numjobs} -C '%1' '%2'
%endif

%description
Filter used by %{chromium_name} to provide content blocking.

%prep
%setup -q -n chromium-%{version}

%if %{use_system_toolchain}
# License: MIT
%autopatch -p1 -m 1000 -M %{_fedoraPatchCount}
%endif

%build
FLAGS=' -Wno-deprecated-declarations -Wno-unknown-warning-option -Wno-unused-command-line-argument'
FLAGS+=' -Wno-unused-but-set-variable -Wno-unused-result -Wno-unused-function -Wno-unused-variable'
FLAGS+=' -Wno-unused-const-variable -Wno-unneeded-internal-declaration -Wno-unknown-attributes -Wno-unknown-pragmas'

CFLAGS="$FLAGS"
CXXFLAGS="$FLAGS"
LDFLAGS="-Wl,-z,now -Wl,-z,pack-relative-relocs"
RUSTFLAGS=${RUSTFLAGS/--cap-lints/-Clink-arg=-Wl,-z,pack-relative-relocs --cap-lints}
RUSTFLAGS=${RUSTFLAGS/debuginfo=?/debuginfo=0}


export CC=clang
export CXX=clang++
export AR=llvm-ar
export NM=llvm-nm
export READELF=llvm-readelf
export CFLAGS
export CXXFLAGS
export LDFLAGS
export RUSTFLAGS

export RUSTC_BOOTSTRAP=1

mkdir -p %{chromebuilddir}

%if %{use_system_toolchain}
declare -r clang_version="$(clang --version | sed -n 's/clang version //p' | cut -d. -f1)"
declare -r clang_base_path="$(PATH=/usr/bin:/usr/sbin which clang | sed 's#/bin/.*##')"
declare -r rust_bindgen_root="$(which bindgen | sed 's#/s\?bin/.*##')"
%else
declare -r present_source_dir="$PWD"
# add internal gn to PATH for build
PATH="$PATH:$present_source_dir/buildtools/linux64"
export PATH
%endif

CHROMIUM_GN_DEFINES=""
%ifarch aarch64
CHROMIUM_GN_DEFINES+=' target_cpu="arm64"'
%endif
%if %{use_system_toolchain}
CHROMIUM_GN_DEFINES+=" custom_toolchain=\"//build/toolchain/linux/unbundle:default\""
CHROMIUM_GN_DEFINES+=" host_toolchain=\"//build/toolchain/linux/unbundle:default\""
CHROMIUM_GN_DEFINES+=" clang_base_path=\"$clang_base_path\""
CHROMIUM_GN_DEFINES+=" clang_version=$clang_version"
CHROMIUM_GN_DEFINES+=" clang_use_chrome_plugins=false"
CHROMIUM_GN_DEFINES+=" rust_sysroot_absolute=\"$(rustc --print sysroot)\""
CHROMIUM_GN_DEFINES+=" rust_bindgen_root=\"$rust_bindgen_root\""
CHROMIUM_GN_DEFINES+=" rustc_version=\"$(rustc --version)\""
%endif
CHROMIUM_GN_DEFINES+=' system_libdir="%{_lib}"'
CHROMIUM_GN_DEFINES+=' is_clang=true'
CHROMIUM_GN_DEFINES+=' use_sysroot=false'
CHROMIUM_GN_DEFINES+=' treat_warnings_as_errors=false'
export CHROMIUM_GN_DEFINES

mkdir -p %{chromebuilddir}

# Build the converter tool
gn --script-executable=%{__python3} gen --args="$CHROMIUM_GN_DEFINES" %{chromebuilddir}

%if %{use_system_toolchain}
%build_target %{chromebuilddir} subresource_filter_tools
%else
%{__python3} $present_source_dir/third_party/depot_tools/autoninja.py -C %{chromebuilddir} subresource_filter_tools
%endif

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
