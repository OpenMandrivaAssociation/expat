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
%global optflags %optflags -O3 -fPIC

# (tpg) enable PGO build
%ifnarch riscv64
%bcond_without pgo
%else
%bcond_with pgo
%endif

Summary:	XML parser written in C
Name:		expat
Version:	2.4.1
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

cd ..
%endif

%if %{with pgo}
%define _vpath_builddir pgo
mkdir pgo
export LLVM_PROFILE_FILE=%{name}-%p.profile.d
export LD_LIBRARY_PATH="$(pwd)"
CFLAGS="%{optflags} -fprofile-instr-generate" \
CXXFLAGS="%{optflags} -fprofile-instr-generate" \
FFLAGS="$CFLAGS" \
FCFLAGS="$CFLAGS" \
LDFLAGS="%{ldflags} -fprofile-instr-generate" \
%cmake \
	-G Ninja
%ninja_build
%ninja_test ||:

unset LD_LIBRARY_PATH
unset LLVM_PROFILE_FILE
llvm-profdata merge --output=%{name}.profile *.profile.d
ninja clean
rm -rf pgo

%undefine _vpath_builddir

CFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
CXXFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
LDFLAGS="%{ldflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
%endif
%cmake -DBUILD_SHARED_LIBS=ON -G Ninja

%if %{with compat32}
%ninja_build -C build32
%endif
%ninja_build -C build

%check
%if %{with compat32}
make check -C build32
%endif
make check -C build

%install
%if %{with compat32}
%ninja_install -C build32 mandir=%{_mandir}/man1
%endif
%ninja_install -C build mandir=%{_mandir}/man1
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
%dir %{_libdir}/cmake/%{name}-%{version}
%{_libdir}/cmake/%{name}-%{version}/*.cmake

%if %{with compat32}
%files -n %{lib32name}
%{_prefix}/lib/libexpat.so.%{major}*

%files -n %{dev32name}
%{_prefix}/lib/libexpat.so
%{_prefix}/lib/pkgconfig/expat.pc
%endif
