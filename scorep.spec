%global shortname scorep
%global ver 1.4.2
%{?altcc_init}

Name:           %{shortname}%{?altcc_pkg_suffix}
Version:        %{ver}
Release:        6%{?dist}
Summary:        Scalable Performance Measurement Infrastructure for Parallel Codes

License:        BSD
URL:            http://www.vi-hps.org/projects/score-p/
Source0:        http://www.vi-hps.org/upload/packages/%{shortname}/%{shortname}-%{version}.tar.gz
Source1:        %{shortname}.module.in
# Fix getaddrinfo() feature test
Patch0:         scorep-getaddrinfo.patch
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  binutils-devel
BuildRequires:  chrpath
# Just use internal cube
BuildRequires:  cube%{?altcc_cc_dep_suffix}-devel >= 4.3
BuildRequires:  opari2
BuildRequires:  otf2-devel >= 1.4
BuildRequires:  papi-devel
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       binutils-devel%{?_isa}
# Just use internal cube
Requires:       cube%{?altcc_cc_dep_suffix}-devel%{?_isa} >= 4.3
Requires:       otf2-devel%{?_isa} >= 1.5
Requires:       papi-devel%{?_isa}
%?altcc_reqmodules
%?altcc_provide


%description
The Score-P (Scalable Performance Measurement Infrastructure for
Parallel Codes) measurement infrastructure is a highly scalable and
easy-to-use tool suite for profiling, event trace recording, and
online analysis of HPC applications.


%package        doc
Summary:        Documentation for %{name}
BuildArch:      noarch
%{?altcc:%altcc_provide doc}

%description    doc
The %{name}-doc package contains documentation for %{name}


%package libs
Summary:        Score-P runtime libraries
%{?altcc:%altcc_provide libs}

%description libs
Score-P runtime libraries.


%prep
%setup -q -n %{shortname}-%{version}
%patch0 -p1 -b .getaddrinfo
# Bundled libs in vendor/
rm -rf vendor/{opari2,otf2}


%build
%global configure_opts --enable-shared --disable-static --disable-silent-rules
%{?altcc:%global configure_opts %{configure_opts} --with-nocross-compiler-suite=%{altcc_cc_name}}
%if !0%{?altcc_with_mpi}
%global configure_opts  %{configure_opts} --without-mpi --without-shmem
%endif
%{?altcc:ml cube}

cp /usr/lib/rpm/redhat/config.{sub,guess} build-config/
unset CFLAGS CXXFLAGS
%configure %{configure_opts}
find -name Makefile -exec sed -r -i 's,-L/usr/%{_lib}/?( |$),,g;s,-L/usr/lib/../%{_lib} ,,g' {} \;
make %{?_smp_mflags}


%install
%make_install
# Install doc
cp -p AUTHORS ChangeLog README THANKS \
      %{buildroot}%{_defaultdocdir}/scorep/
find %{buildroot} -name '*.la' -exec rm -f {} ';'

%{?altcc:%altcc_doc}
%{?altcc:%altcc_license}
%{?altcc:%altcc_writemodule %SOURCE1}


%files
%{?altcc:%altcc_files -dl %{_bindir} %{_includedir}}
%license COPYING
%dir %{_defaultdocdir}/scorep
%{_defaultdocdir}/scorep/AUTHORS
%{_defaultdocdir}/scorep/ChangeLog
%{_defaultdocdir}/scorep/README
%{_defaultdocdir}/scorep/THANKS
%{_bindir}/online-access-registry
%{_bindir}/scorep
%{_bindir}/scorep-backend-info
%{_bindir}/scorep-config
%{_bindir}/scorep-info
%{_bindir}/scorep-score
%{_datadir}/scorep/
%{_includedir}/scorep/

%files doc
%{_defaultdocdir}/scorep/

%files libs
%{?altcc:%altcc_files -lm %{_libdir}}
%license COPYING
%{_libdir}/lib*.so*


%changelog
* Fri Feb 19 2016 Dave Love <loveshack@fedoraproject.org> - 1.4.2-6
- Link against papi-5.1.1 on el6
- Link --as-needed (see previous rpmlint warnings)
- Install OPEN_ISSUES as doc
- Use -std=gnu++98 for gcc6

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jan 27 2016 Orion Poplawski <orion@cora.nwra.com> - 1.4.2-4
- Rebuild for papi 5.4.3

* Wed Sep 16 2015 Orion Poplawski <orion@cora.nwra.com> - 1.4.2-3
- Rebuild for openmpi 1.10.0

* Wed Aug 12 2015 Orion Poplawski <orion@cora.nwra.com> - 1.4.2-3
- Add patch to handle glibc 2.22 change to getaddrinfo() exposure

* Sun Jul 26 2015 Sandro Mani <manisandro@gmail.com> - 1.4.2-2
- Rebuild for RPM MPI Requires Provides Change

* Fri Jun 19 2015 Orion Poplawski <orion@cora.nwra.com> - 1.4.2-1
- Update to 1.4.2

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon May 11 2015 Orion Poplawski <orion@cora.nwra.com> - 1.4.1-2
- Require papi-devel, add requires to mpi packages

* Fri May 8 2015 Orion Poplawski <orion@cora.nwra.com> - 1.4.1-1
- Update to 1.4.1

* Tue May 5 2015 Orion Poplawski <orion@cora.nwra.com> - 1.4-1
- Update to 1.4

* Sun May  3 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 1.3-7
- Rebuild for changed mpich

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 1.3-6
- Rebuilt for GCC 5 C++11 ABI change

* Fri Mar 13 2015 Orion Poplawski <orion@cora.nwra.com> - 1.3-5
- Rebuild for mpich 3.1.4 soname change

* Wed Mar 04 2015 Orion Poplawski <orion@cora.nwra.com> - 1.3-4
- Rebuild for papi

* Mon Jan 19 2015 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> - 1.3-3
- update gnu-config files to build on aarch64

* Sat Dec 13 2014 Orion Poplawski <orion@cora.nwra.com> - 1.3-2
- Use %%license

* Fri Oct 3 2014 Orion Poplawski <orion@cora.nwra.com> - 1.3-1
- Update to 1.3

* Tue Mar 4 2014 Orion Poplawski <orion@cora.nwra.com> - 1.2.3-2
- Split out runtime libraries in libs sub-packages
- Fix doc duplication
- Use chrpath to remove rpaths

* Wed Feb 26 2014 Orion Poplawski <orion@cora.nwra.com> - 1.2.3-1
- Update to 1.2.3

* Tue Dec 17 2013 Orion Poplawski <orion@cora.nwra.com> - 1.2.2-1
- Update to 1.2.2
- Drop path patch fixed upstream
- Drop rpath issue fixes, fixed upstream

* Wed Sep 25 2013 Orion Poplawski <orion@cora.nwra.com> - 1.2.1-1
- Initial package
