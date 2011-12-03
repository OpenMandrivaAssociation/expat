%define libname_orig libexpat
%define major 1
%define libname %mklibname expat %{major}
%define develname %mklibname expat -d

Summary:	XML parser written in C
Name:		expat
Version:	2.0.1
Release:	16
License:	MPL or GPL
Group:		System/Libraries
URL:		http://www.libexpat.org
Source0:	http://prdownloads.sourceforge.net/expat/expat-%{version}.tar.bz2
Patch0:		expat-2.0.1-CVE-2009-3720.diff
Patch1:		expat-2.0.1-CVE-2009-3560.diff
Patch2:		expat-2.0.1-confcxx.patch
BuildRequires:	autoconf automake libtool
Requires:	%{libname} >= %{version}-%{release}

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
%patch0 -p0 -b .CVE-2009-3720
%patch1 -p0 -b .CVE-2009-3560
%patch2 -p1 -b .confcxx

%build
rm -rf autom4te*.cache
rm conftools/libtool.m4
libtoolize --copy --force --automake; aclocal; autoheader; autoconf
export CFLAGS="%{optflags} -fPIC"

%configure2_5x
%make

%check
make check

%install
rm -rf %{buildroot}

%makeinstall_std mandir=%{buildroot}%{_mandir}/man1

# cleanup
rm -rf %{buildroot}%{_libdir}/*.*a

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
