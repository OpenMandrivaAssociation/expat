%define date 2007-06-05
%define libname_orig libexpat
%define major 1
%define libname %mklibname expat %{major}

Summary:        Expat is an XML parser written in C
Name:           expat
Version:        2.0.1
Release:        %mkrel 2
License:        MPL or GPL
Group:          Development/Other
URL:            http://www.jclark.com/xml/expat.html
Source0         http://prdownloads.sourceforge.net/expat/expat-%{version}.tar.gz
Requires:       %{libname} = %{version}-%{release}
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
Expat is an XML 1.0 parser written in C by James Clark.  It aims to be
fully conforming. It is currently not a validating XML parser.

%package -n %{libname}
Summary:        Main library for expat
Group:          Development/C

%description -n %{libname}
This package contains the library needed to run programs dynamically
linked with expat.

%package -n %{libname}-devel
Summary:        Development environment for the expat XML parser
Group:          Development/C
Requires:       %{libname} = %{version}
Provides:       %{libname_orig}-devel = %{version}-%{release}
Provides:       %{name}-devel = %{version}-%{release}
Obsoletes:      %{name}-devel < %{version}-%{release}

%description -n %{libname}-devel
Development environment for the expat XML parser

%prep
%setup -q -n expat-%{date}

%build
%{configure2_5x}
%{make}
 
%install
%{__rm} -rf %{buildroot}

%{makeinstall} man1dir=%{buildroot}%{_mandir}/man1
#%{__rm} -f %{buildroot}%{_mandir}/xmlwf.1*

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root)
%{_bindir}/xmlwf
%{_mandir}/man*/*

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/libexpat.so.*

%files -n %{libname}-devel
%defattr(-,root,root)
%doc doc/reference.html
%{_libdir}/libexpat.so
%{_includedir}/expat.h
%{_includedir}/expat_external.h
%{_libdir}/libexpat.a
%{_libdir}/libexpat.la
