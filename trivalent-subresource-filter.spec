%global numjobs %{_smp_build_ncpus}
%global chromebuilddir out/Release
%global _default_patch_fuzz 2
%global chromium_name trivalent
%global debug_package %{nil}

Source69: chromium-version.txt

Name:      %{chromium_name}-subresource-filter
Requires:  %{chromium_name}
BuildArch: noarch
License:   Apache-2.0
Summary:   Subresource filter for %{chromium_name}
%{lua:
        local f = io.open(macros['_sourcedir']..'/chromium-version.txt', 'r')
        local version_tag = f:read "*all"

        -- This IS NOT the version of the browser
        -- It is only used if it is greater than the automated version detection
        -- The point is to update to an arbitrary greater release tag, like early stable or beta tags
        local off_version_tag = "141.0.7390.127" -- "142.0.7444.52"

        -- Strip the dots to make it just a number and compare
        -- If greater than, we use the off-version
        if string.gsub(off_version_tag, "%.", "") > string.gsub(version_tag, "%.", "") then
            version_tag = off_version_tag
        end

        -- This will dynamically set the version based on chromium's latest stable release channel
        print("Version: "..version_tag.."\n")

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

Patch0: use-cwd-for-gclient-path.patch

%description
Filter used by %{chromium_name} to provide content blocking.

%prep
%setup -q -n chromium-%{version}

%patch -P0 -p1 -b .use-cwd-for-gclient-path

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
declare -r present_source_dir="$PWD"
# add internal gn to PATH for build
PATH="$PATH:$present_source_dir/buildtools/linux64"
export PATH

# Disable libcxx modules
sed -i -e "s/use_libcxx_modules = is_clang/use_libcxx_modules = false/g" $present_source_dir/build/config/BUILDCONFIG.gn

CHROMIUM_GN_DEFINES=""
CHROMIUM_GN_DEFINES+=' system_libdir="%{_lib}"'
CHROMIUM_GN_DEFINES+=' is_clang=true'
CHROMIUM_GN_DEFINES+=' use_sysroot=false'
CHROMIUM_GN_DEFINES+=' treat_warnings_as_errors=false'
export CHROMIUM_GN_DEFINES

mkdir -p %{chromebuilddir}

# Build the converter tool
gn --script-executable=%{__python3} gen --args="$CHROMIUM_GN_DEFINES" %{chromebuilddir}

%{__python3} $present_source_dir/third_party/depot_tools/autoninja.py -C %{chromebuilddir} subresource_filter_tools

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
