# expat is used by dbus, which is used by wine and steam
%ifarch %{x86_64}
%bcond_without compat32
%else
%bcond_with compat32
%endif

%define major 1
%define libname %mklibname expat %{major}
%define devname %mklibname expat -d
%define lib32name libexpat%{major}
%define dev32name libexpat-devel

# (tpg) optimize it a bit
%global optflags %{optflags} -O3 -fPIC

# (tpg) enable PGO build
%if %{cross_compiling}
%bcond_with pgo
%else
%bcond_without pgo
%endif

Summary:	XML parser written in C
Name:		expat
Version:	2.8.4
Release:	1
License:	MPL or GPLv2
Group:		System/Libraries
Url:		https://www.libexpat.org
Source0:	http://prdownloads.sourceforge.net/expat/%{name}-%{version}.tar.xz
Source1:	%{name}.rpmlintrc
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	docbook-utils
BuildRequires:	xmlto
%if %{with compat32}
# clang -m32 reads i386-*.cfg (--sysroot /usr/i686-openmandriva-linux-gnu).
# binutils ships the usr -> ./ symlink so lld can resolve the absolute
# paths in the sysroot's libc.so linker script.
BuildRequires:	cross-i686-openmandriva-linux-gnu-clang
BuildRequires:	cross-i686-openmandriva-linux-gnu-libc
BuildRequires:	cross-i686-openmandriva-linux-gnu-gcc
BuildRequires:	cross-i686-openmandriva-linux-gnu-binutils
%endif

%description
Expat is an XML 1.0 parser written in C by James Clark.  It aims to be
fully conforming. It is currently not a validating XML parser.

%package -n %{libname}
Summary:	Main library for expat
Group:		System/Libraries

%description -n %{libname}
This package contains the library needed to run programs dynamically
linked with expat.

%package -n %{devname}
Summary:	Development environment for the expat XML parser
Group:		Development/C
Requires:	%{libname} >= %{EVRD}
Provides:	%{name}-devel = %{EVRD}
Obsoletes:	%{mklibname expat -d 1} < 2.2.4

%description -n %{devname}
Development environment for the expat XML parser.

%if %{with compat32}
%package -n %{lib32name}
Summary:	Main library for expat (32-bit)
Group:		System/Libraries
BuildRequires:	libc6
Requires:	libc6

%description -n %{lib32name}
This package contains the library needed to run programs dynamically
linked with expat.

%package -n %{dev32name}
Summary:	Development environment for the expat XML parser
Group:		Development/C
Requires:	%{lib32name} = %{EVRD}
Requires:	%{devname} = %{EVRD}

%description -n %{dev32name}
Development environment for the expat XML parser.
%endif

%prep
%autosetup -p1

%build
%if %{with compat32}
%cmake32 \
	-G Ninja

%ninja_build
cd ..
%endif

%if %{with pgo}
CFLAGS="%{optflags} -fprofile-generate" \
CXXFLAGS="%{optflags} -fprofile-generate" \
LDFLAGS="%{build_ldflags} -fprofile-generate" \
%cmake \
	-G Ninja

%ninja_build
export LD_LIBRARY_PATH="$(pwd)${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
# Typical well-formed traffic (dbus / config / appstream-like). The
# test suite overweights error paths and is a poor PGO profile.
train=../pgo-train
mkdir -p "$train"
cat > "$train/dbus.xml" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<node name="/org/freedesktop/DBus">
	<interface name="org.freedesktop.DBus.Introspectable">
		<method name="Introspect">
			<arg name="xml_data" type="s" direction="out"/>
		</method>
	</interface>
	<interface name="org.freedesktop.DBus.Properties">
		<method name="Get">
			<arg name="interface_name" type="s" direction="in"/>
			<arg name="property_name" type="s" direction="in"/>
			<arg name="value" type="v" direction="out"/>
		</method>
		<method name="GetAll">
			<arg name="interface_name" type="s" direction="in"/>
			<arg name="props" type="a{sv}" direction="out"/>
		</method>
		<signal name="PropertiesChanged">
			<arg name="interface_name" type="s"/>
			<arg name="changed_properties" type="a{sv}"/>
			<arg name="invalidated_properties" type="as"/>
		</signal>
	</interface>
	<node name="Bus"/>
</node>
EOF
cat > "$train/config.xml" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
	<server host="localhost" port="8080" ssl="false">
		<timeout>30</timeout>
		<workers>8</workers>
		<listen address="::" backlog="128"/>
	</server>
	<log level="info" path="/var/log/app.log"/>
	<users>
		<user id="1" name="root" enabled="true"><email>root@example.com</email></user>
		<user id="2" name="alice" enabled="true"><email>alice@example.com</email></user>
		<user id="3" name="café" enabled="false"><email>cafe@example.com</email></user>
	</users>
</configuration>
EOF
cat > "$train/appstream.xml" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<components version="0.14" origin="openmandriva">
	<component type="desktop-application">
		<id>org.example.App</id>
		<name>Example App</name>
		<summary>A typical desktop application</summary>
		<description><p>Short description with <em>inline</em> markup and UTF-8 café.</p></description>
		<url type="homepage">https://example.com/</url>
		<provides><binary>example</binary></provides>
		<releases>
			<release version="1.2.3" date="2026-08-01"/>
			<release version="1.2.2" date="2026-07-01"/>
		</releases>
	</component>
</components>
EOF
{
	echo '<?xml version="1.0" encoding="UTF-8"?>'
	echo '<catalog xmlns="http://example.com/ns" xmlns:x="http://example.com/x">'
	i=0
	while [ $i -lt 4000 ]; do
		echo "<item id=\"$i\" name=\"entry-$i\" enabled=\"true\"><title>Item $i</title><desc>Typical text for item $i (café 日本語)</desc><x:meta k=\"v$i\"/></item>"
		i=$((i + 1))
	done
	echo '</catalog>'
} > "$train/large.xml"
xmlwf=./xmlwf/xmlwf
i=0
while [ $i -lt 40 ]; do
	"$xmlwf" -t "$train/dbus.xml" "$train/config.xml" "$train/appstream.xml"
	"$xmlwf" -t -n "$train/dbus.xml" "$train/appstream.xml" "$train/large.xml"
	"$xmlwf" -t -r "$train/dbus.xml" "$train/config.xml"
	i=$((i + 1))
done
i=0
while [ $i -lt 8 ]; do
	"$xmlwf" -t "$train/large.xml"
	"$xmlwf" -t -r -g 8192 "$train/large.xml"
	i=$((i + 1))
done
unset LD_LIBRARY_PATH
llvm-profdata merge --output=../%{name}-llvm.profdata $(find . -name "*.profraw" -type f)
PROFDATA="$(realpath ../%{name}-llvm.profdata)"
rm -f *.profraw
ninja clean
cd ..
rm -rf build

CFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
CXXFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
LDFLAGS="%{build_ldflags} -fprofile-use=$PROFDATA" \
%endif
%cmake -DBUILD_SHARED_LIBS=ON -G Ninja

%ninja_build
cd ..

%if ! %{cross_compiling}
%check
%if %{with compat32}
%ninja_test -C build32
%endif
%ninja_test -C build
%endif

%install
%if %{with compat32}
%ninja_install -C build32
%endif
%ninja_install -C build
rm -rf %{buildroot}%{_docdir}/%{name}

%files
%{_bindir}/xmlwf
%doc %{_mandir}/man*/*

%files -n %{libname}
%{_libdir}/libexpat.so.%{major}*

%files -n %{devname}
%doc doc/reference.html
%{_libdir}/libexpat.so
%{_includedir}/expat.h
%{_includedir}/expat_config.h
%{_includedir}/expat_external.h
%{_libdir}/pkgconfig/expat.pc
%dir %{_libdir}/cmake/%{name}-%{version}
%{_libdir}/cmake/%{name}-%{version}/*.cmake

%if %{with compat32}
%files -n %{lib32name}
%{_prefix}/lib/libexpat.so.%{major}*

%files -n %{dev32name}
%{_prefix}/lib/libexpat.so
%{_prefix}/lib/pkgconfig/expat.pc
%dir %{_prefix}/lib/cmake/%{name}-%{version}
%{_prefix}/lib/cmake/%{name}-%{version}/*.cmake
%endif
