Name:           scorep
Version:        1.4.2
Release:        2%{?dist}
Summary:        Scalable Performance Measurement Infrastructure for Parallel Codes

License:        BSD
URL:            http://www.vi-hps.org/projects/score-p/
Source0:        http://www.vi-hps.org/upload/packages/%{name}/%{name}-%{version}.tar.gz
BuildRequires:  gcc-gfortran
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  binutils-devel
BuildRequires:  chrpath
BuildRequires:  cube-devel >= 4.3
BuildRequires:  opari2
BuildRequires:  otf2-devel >= 1.4
BuildRequires:  papi-devel
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       binutils-devel%{?_isa}
Requires:       cube-devel%{?_isa} >= 4.3
Requires:       otf2-devel%{?_isa} >= 1.5
Requires:       papi-devel%{?_isa}

%global with_mpich 1
%global with_openmpi 1
%ifarch s390 s390x
# No openmpi on s390(x)
%global with_openmpi 0
%endif
# No mpich on EL6 ppc64
%ifarch ppc64
%if 0%{?rhel} && 0%{?rhel} <= 6
%global with_mpich 0
%endif
%endif

%if %{with_mpich}
%global mpi_list mpich
%endif
%if %{with_openmpi}
%global mpi_list %{?mpi_list} openmpi
%endif

%description
The Score-P (Scalable Performance Measurement Infrastructure for
Parallel Codes) measurement infrastructure is a highly scalable and
easy-to-use tool suite for profiling, event trace recording, and
online analysis of HPC applications.


%package        doc
Summary:        Documentation for %{name}
BuildArch:      noarch

%description    doc
The %{name}-doc package contains documentation for %{name}


%package libs
Summary:        Score-P runtime libraries

%description libs
Score-P runtime libraries.

%if %{with_mpich}
%package mpich
Summary:        Scalable Performance Measurement Infrastructure for Parallel Codes for mpich
BuildRequires:  mpich-devel
Requires:       %{name}-mpich-libs%{?_isa} = %{version}-%{release}
Requires:       cube-devel%{?_isa} >= 4.3
Requires:       otf2-devel%{?_isa} >= 1.5
Requires:       papi-devel%{?_isa}

%description mpich
The Score-P (Scalable Performance Measurement Infrastructure for
Parallel Codes) measurement infrastructure is a highly scalable and
easy-to-use tool suite for profiling, event trace recording, and
online analysis of HPC applications.

This package was compiled with mpich.


%package mpich-libs
Summary:        Score-P mpich runtime libraries

%description mpich-libs
Score-P mpich runtime libraries.
%endif


%if %{with_openmpi}
%package openmpi
Summary:        Scalable Performance Measurement Infrastructure for Parallel Codes for openmpi
BuildRequires:  openmpi-devel
Requires:       %{name}-openmpi-libs%{?_isa} = %{version}-%{release}
Requires:       cube-devel%{?_isa} >= 4.3
Requires:       otf2-devel%{?_isa} >= 1.5
Requires:       papi-devel%{?_isa}

%description openmpi
The Score-P (Scalable Performance Measurement Infrastructure for
Parallel Codes) measurement infrastructure is a highly scalable and
easy-to-use tool suite for profiling, event trace recording, and
online analysis of HPC applications.

This package was compiled with openmpi.

%package openmpi-libs
Summary:        Score-P openmpi runtime libraries

%description openmpi-libs
Score-P openmpi runtime libraries.
%endif


%prep
%setup -q
# Bundled libs in vendor/
rm -rf vendor/{opari2,otf2}


%build
%global _configure ../configure
%global configure_opts --enable-shared --disable-static --disable-silent-rules

cp /usr/lib/rpm/redhat/config.{sub,guess} build-config/

# Build serial version
mkdir serial
cd serial
%configure %{configure_opts} --without-mpi --without-shmem
make %{?_smp_mflags}
cd -

# Build MPI versions
for mpi in %{mpi_list}
do
  mkdir $mpi
  cd $mpi
%if 0%{?el6}
  module load $mpi-%{_arch}
%else
  module load mpi/$mpi-%{_arch}
%endif
  ln -s ../configure .
  %configure %{configure_opts} \
    --libdir=%{_libdir}/$mpi/lib \
    --bindir=%{_libdir}/$mpi/bin \
    --sbindir=%{_libdir}/$mpi/sbin \
    --includedir=%{_includedir}/$mpi-%{_arch} \
    --mandir=%{_libdir}/$mpi/share/man
  make %{?_smp_mflags}
  module purge
  cd -
done


%install
%make_install -C serial
# Install doc
cp -p AUTHORS ChangeLog README THANKS \
      %{buildroot}%{_defaultdocdir}/scorep/
# Strip rpath
chrpath -d %{buildroot}%{_libdir}/*.so.*

for mpi in %{mpi_list}
do
%if 0%{?el6}
  module load $mpi-%{_arch}
%else
  module load mpi/$mpi-%{_arch}
%endif
  %make_install -C $mpi
  module purge
done
find %{buildroot} -name '*.la' -exec rm -f {} ';'


%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig


%files
%{!?_licensedir:%global license %%doc}
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
%license COPYING
%{_libdir}/libscorep_*.so*

%if %{with_mpich}
%files mpich
%license COPYING
%doc AUTHORS ChangeLog README THANKS
%{_libdir}/mpich/bin/online-access-registry
%{_libdir}/mpich/bin/scorep
%{_libdir}/mpich/bin/scorep-backend-info
%{_libdir}/mpich/bin/scorep-config
%{_libdir}/mpich/bin/scorep-info
%{_libdir}/mpich/bin/scorep-score
%{_includedir}/mpich-%{_arch}/scorep/

%files mpich-libs
%{_libdir}/mpich/lib/*.so*
%endif

%if %{with_openmpi}
%files openmpi
%license COPYING
%doc AUTHORS ChangeLog README THANKS
%{_libdir}/openmpi/bin/online-access-registry
%{_libdir}/openmpi/bin/scorep
%{_libdir}/openmpi/bin/scorep-backend-info
%{_libdir}/openmpi/bin/scorep-config
%{_libdir}/openmpi/bin/scorep-info
%{_libdir}/openmpi/bin/scorep-score
%{_includedir}/openmpi-%{_arch}/scorep/

%files openmpi-libs
%{_libdir}/openmpi/lib/*.so*
%endif

%changelog
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
