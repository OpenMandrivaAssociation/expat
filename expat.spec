%define	major	1
%define libname	%mklibname expat %{major}
%define	devname	%mklibname expat -d

# (tpg) optimize it a bit
%global optflags %optflags -O3

Summary:	XML parser written in C
Name:		expat
Version:	2.2.4
Release:	1
License:	MPL or GPLv2
Group:		System/Libraries
Url:		http://www.libexpat.org
Source0:	http://prdownloads.sourceforge.net/expat/%{name}-%{version}.tar.bz2
Source1:	%{name}.rpmlintrc
BuildRequires:	libtool

%description
Expat is an XML 1.0 parser written in C by James Clark.  It aims to be
fully conforming. It is currently not a validating XML parser.

%package -n	%{libname}
Summary:	Main library for expat
Group:		System/Libraries

%description -n	%{libname}
This package contains the library needed to run programs dynamically
linked with expat.

%package -n	%{devname}
Summary:	Development environment for the expat XML parser
Group:		Development/C
Requires:	%{libname} >= %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{mklibname expat -d 1} < 2.2.4

%description -n	%{devname}
Development environment for the expat XML parser.

%prep
%setup -q
%apply_patches

%build
export CFLAGS="%{optflags} -fPIC"

%configure \
	--disable-static

%make

%check
make check

%install
%makeinstall_std mandir=%{_mandir}/man1
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
