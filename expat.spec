%define libname_orig libexpat
%define major 0
%define libname %mklibname %{name} %{major}

Summary:	Expat is an XML parser written in C
Name:		expat
Version:	1.95.8
Release:	%mkrel 4
License:	MPL or GPL
Group:		Development/Other
URL:		http://www.jclark.com/xml/expat.html
Source:		http://prdownloads.sourceforge.net/expat/%{name}-%{version}.tar.bz2
Requires:	%{libname} = %{version}-%{release}
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Expat is an XML 1.0 parser written in C by James Clark.  It aims to be
fully conforming. It is currently not a validating XML parser.

%package -n	%{libname}
Summary:	Main library for expat
Group:		Development/C
Obsoletes:	libexpat1_95
Provides:	libexpat1_95 = %{version}-%{release}

%description -n %{libname}
This package contains the library needed to run programs dynamically
linked with expat.

%package -n	%{libname}-devel
Summary:	Development environment for the expat XML parser
Group:		Development/C
Requires:	%{libname} = %{version}
Provides:       %{libname_orig}-devel = %{version}-%{release} %{name}-devel = %{version}-%{release}
Obsoletes:      %{name}-devel
Obsoletes:      libexpat1_95-devel
Provides:       libexpat1_95-devel = %{version}-%{release}

%description -n	%{libname}-devel
Development environment for the expat XML parser

%prep
%setup -q

%build
%configure2_5x
%make
 
%install
rm -rf %{buildroot}

%makeinstall man1dir=%{buildroot}%{_mandir}/man1
#rm -f %{buildroot}%{_mandir}/xmlwf.1*

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%clean
rm -rf %{buildroot}

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


