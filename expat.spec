%define libname_orig libexpat
%define major 1
%define libname %mklibname expat %{major}
%define develname %mklibname expat -d

Summary:	XML parser written in C
Name:		expat
Version:	2.1.0
Release:	1
License:	MPL or GPL
Group:		System/Libraries
URL:		http://www.libexpat.org
Source0:	http://prdownloads.sourceforge.net/expat/expat-%{version}.tar.gz
BuildRequires:	libtool

%description
Expat is an XML 1.0 parser written in C by James Clark.  It aims to be
fully conforming. It is currently not a validating XML parser.

%package -n %{libname}
Summary:	Main library for expat
Group:		System/Libraries

%description -n %{libname}
This package contains the library needed to run programs dynamically
linked with expat.

%package -n %{develname}
Summary:	Development environment for the expat XML parser
Group:		Development/C
Requires:       %{libname} >= %{version}-%{release}
Provides:	%{libname_orig}-devel = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{mklibname expat -d 0}
Provides:	%{mklibname expat -d 0} = %{version}-%{release}
Obsoletes:	%{mklibname expat -d 1}

%description -n %{develname}
Development environment for the expat XML parser.

%prep

%setup -q

%build
export CFLAGS="%{optflags} -fPIC"

%configure2_5x --disable-static
%make

%check
make check

%install
%makeinstall_std mandir=%{buildroot}%{_mandir}/man1

# cleanup
rm -rf %{buildroot}%{_libdir}/*.la

%files
%{_bindir}/xmlwf
%{_mandir}/man*/*

%files -n %{libname}
%{_libdir}/libexpat.so.%{major}*

%files -n %{develname}
%doc doc/reference.html
%{_libdir}/libexpat.so
%{_includedir}/expat.h
%{_includedir}/expat_external.h
%{_libdir}/pkgconfig/expat.pc

