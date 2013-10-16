%define	major	1
%define libname	%mklibname expat %{major}
%define	devname	%mklibname expat -d

%bcond_without	uclibc

Summary:	XML parser written in C
Name:		expat
Version:	2.1.0
Release:	5
License:	MPL or GPLv2
Group:		System/Libraries
Url:		http://www.libexpat.org
Source0:	http://prdownloads.sourceforge.net/expat/%{name}-%{version}.tar.gz
Patch0:		expat-aarch64.patch

BuildRequires:	libtool
%if %{with uclibc}
BuildRequires:	uClibc-devel >= 0.9.33.2-9
%endif

%description
Expat is an XML 1.0 parser written in C by James Clark.  It aims to be
fully conforming. It is currently not a validating XML parser.

%package -n	%{libname}
Summary:	Main library for expat
Group:		System/Libraries

%description -n	%{libname}
This package contains the library needed to run programs dynamically
linked with expat.

%if %{with uclibc}
%package -n	uclibc-%{libname}
Summary:	Main library for expat
Group:		System/Libraries

%description -n	uclibc-%{libname}
This package contains the library needed to run programs dynamically
linked with expat.
%endif

%package -n	%{devname}
Summary:	Development environment for the expat XML parser
Group:		Development/C
Requires:	%{libname} >= %{version}-%{release}
%if %{with uclibc}
Requires:	uclibc-%{libname} >= %{version}-%{release}
%endif
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{mklibname expat -d 1}

%description -n	%{devname}
Development environment for the expat XML parser.

%prep
%setup -q
%apply_patches

%build
export CFLAGS="%{optflags} -fPIC"
export CONFIGURE_TOP="$PWD"

%if %{with uclibc}
mkdir -p uclibc
pushd uclibc
%uclibc_configure \
	--disable-static
%make
popd
%endif

mkdir -p shared
pushd shared
%configure2_5x \
	--disable-static
%make
popd

%check
make -C shared check

%install
%if %{with uclibc}
%makeinstall_std -C uclibc mandir=%{buildroot}%{_mandir}/man1
rm -r %{buildroot}%{uclibc_root}{%{_libdir}/pkgconfig,%{_bindir}}
%endif

%makeinstall_std -C shared mandir=%{buildroot}%{_mandir}/man1

%files
%{_bindir}/xmlwf
%{_mandir}/man*/*

%files -n %{libname}
%{_libdir}/libexpat.so.%{major}*

%if %{with uclibc}
%files -n uclibc-%{libname}
%{uclibc_root}%{_libdir}/libexpat.so.%{major}*
%endif

%files -n %{devname}
%doc doc/reference.html
%{_libdir}/libexpat.so
%if %{with uclibc}
%{uclibc_root}%{_libdir}/libexpat.so
%endif
%{_includedir}/expat.h
%{_includedir}/expat_external.h
%{_libdir}/pkgconfig/expat.pc

