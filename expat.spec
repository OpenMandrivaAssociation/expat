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
%bcond_without pgo

Summary:	XML parser written in C
Name:		expat
Version:	2.4.9
Release:	1
License:	MPL or GPLv2
Group:		System/Libraries
Url:		http://www.libexpat.org
Source0:	http://prdownloads.sourceforge.net/expat/%{name}-%{version}.tar.xz
Source1:	%{name}.rpmlintrc
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	docbook-utils
BuildRequires:	xmlto

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
export LD_LIBRARY_PATH="$(pwd)"

CFLAGS="%{optflags} -fprofile-generate" \
CXXFLAGS="%{optflags} -fprofile-generate" \
LDFLAGS="%{build_ldflags} -fprofile-generate" \
%cmake \
	-G Ninja

%ninja_build
%ninja_test ||:

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

%check
%if %{with compat32}
%ninja_test -C build32
%endif
%ninja_test -C build

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
