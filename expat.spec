%define major 1
%define libname %mklibname expat %{major}
%define devname %mklibname expat -d

# (tpg) optimize it a bit
%global optflags %optflags -O3 -fPIC

# (tpg) enable PGO build
%ifnarch riscv64
%bcond_without pgo
%else
%bcond_with pgo
%endif

Summary:	XML parser written in C
Name:		expat
Version:	2.2.8
Release:	1
License:	MPL or GPLv2
Group:		System/Libraries
Url:		http://www.libexpat.org
Source0:	http://prdownloads.sourceforge.net/expat/%{name}-%{version}.tar.xz
Source1:	%{name}.rpmlintrc
BuildRequires:	libtool
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

%prep
%autosetup -p1

%build
%if %{with pgo}
CFLAGS_PGO="%{optflags} -fprofile-instr-generate"
CXXFLAGS_PGO="%{optflags} -fprofile-instr-generate"
FFLAGS_PGO="$CFLAGS_PGO"
FCFLAGS_PGO="$CFLAGS_PGO"
LDFLAGS_PGO="%{ldflags} -fprofile-instr-generate"
export LLVM_PROFILE_FILE=%{name}-%p.profile.d
export LD_LIBRARY_PATH="$(pwd)"

CFLAGS="${CFLAGS_PGO}" CXXFLAGS="${CXXFLAGS_PGO}" FFLAGS="${FFLAGS_PGO}" FCFLAGS="${FCFLAGS_PGO}" LDFLAGS="${LDFLAGS_PGO}" CC="%{__cc}" %configure --disable-static --without-docbook --without-xmlwf
CFLAGS="${CFLAGS_PGO}" CXXFLAGS="${CXXFLAGS_PGO}" FFLAGS="${FFLAGS_PGO}" FCFLAGS="${FCFLAGS_PGO}" LDFLAGS="${LDFLAGS_PGO}" CC="%{__cc}" make check

unset LD_LIBRARY_PATH
unset LLVM_PROFILE_FILE
llvm-profdata merge --output=%{name}.profile *.profile.d
rm -f *.profile.d
make clean

CFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
CXXFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
LDFLAGS="%{ldflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
%endif
%configure \
	--disable-static

%make_build

%check
make check

%install
%make_install mandir=%{_mandir}/man1
rm -rf %{buildroot}%{_docdir}/%{name}

%files
%{_bindir}/xmlwf
%{_mandir}/man*/*

%files -n %{libname}
%{_libdir}/libexpat.so.%{major}*

%files -n %{devname}
%doc doc/reference.html
%{_libdir}/libexpat.so
%{_includedir}/expat.h
%{_includedir}/expat_config.h
%{_includedir}/expat_external.h
%{_libdir}/pkgconfig/expat.pc
