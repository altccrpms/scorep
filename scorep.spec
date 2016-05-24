Name:           scorep
Version:        2.0.2
Release:        1%{?dist}
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
BuildRequires:  otf2-devel >= 2.0
BuildRequires:  papi-devel
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       binutils-devel%{?_isa}
Requires:       cube-devel%{?_isa} >= 4.3
Requires:       otf2-devel%{?_isa} >= 2.0
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
# required for gcc6
export CXXFLAGS=-std=gnu++98
# The messging with linkage paths here and below is due to the mess of
# the papi package there.  %%_libdir/libpapi.so is papi v4 with a
# soname of libpapi.so (bz #1300664).
export LDFLAGS='-Wl,--as-needed -L%{_libdir}/papi-5.1.1/usr/lib'
%global configure_opts --enable-shared --disable-static --disable-silent-rules %{?el6:--with-papi-header=%{_libdir}/papi-5.1.1%{_includedir} --with-papi-lib=%{_libdir}/papi-5.1.1/usr/lib}

cp /usr/lib/rpm/redhat/config.{sub,guess} build-config/

# Build serial version
mkdir serial
cd serial
%configure %{configure_opts} --without-mpi --without-shmem
find -name Makefile -exec sed -r -i 's,-L%{_libdir}/?( |$),,g;s,-L/usr/lib/../%{_lib} ,,g' {} \;
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
  find -name Makefile -exec sed -r -i 's,-L%{_libdir}/?( |$),,g;s,-L/usr/lib/../%{_lib} ,,g' {} \;
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
%{_bindir}/scorep
%{_bindir}/scorep-backend-info
%{_bindir}/scorep-config
%{_bindir}/scorep-g++
%{_bindir}/scorep-gcc
%{_bindir}/scorep-gfortran
%{_bindir}/scorep-info
%{_bindir}/scorep-score
%{_bindir}/scorep-wrapper
%{_libdir}/scorep/
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
%doc AUTHORS ChangeLog README THANKS OPEN_ISSUES
%{_libdir}/mpich/bin/scorep
%{_libdir}/mpich/bin/scorep-backend-info
%{_libdir}/mpich/bin/scorep-config
%{_libdir}/mpich/bin/scorep-g++
%{_libdir}/mpich/bin/scorep-gcc
%{_libdir}/mpich/bin/scorep-gfortran
%{_libdir}/mpich/bin/scorep-info
%{_libdir}/mpich/bin/scorep-mpicc
%{_libdir}/mpich/bin/scorep-mpicxx
%{_libdir}/mpich/bin/scorep-mpif77
%{_libdir}/mpich/bin/scorep-mpif90
%{_libdir}/mpich/bin/scorep-score
%{_libdir}/mpich/bin/scorep-wrapper
%{_libdir}/mpich/lib/scorep/
%{_includedir}/mpich-%{_arch}/scorep/

%files mpich-libs
%{_libdir}/mpich/lib/*.so*
%endif

%if %{with_openmpi}
%files openmpi
%license COPYING
%doc AUTHORS ChangeLog README THANKS OPEN_ISSUES
%{_libdir}/openmpi/bin/scorep
%{_libdir}/openmpi/bin/scorep-backend-info
%{_libdir}/openmpi/bin/scorep-config
%{_libdir}/openmpi/bin/scorep-g++
%{_libdir}/openmpi/bin/scorep-gcc
%{_libdir}/openmpi/bin/scorep-gfortran
%{_libdir}/openmpi/bin/scorep-info
%{_libdir}/openmpi/bin/scorep-mpicc
%{_libdir}/openmpi/bin/scorep-mpicxx
%{_libdir}/openmpi/bin/scorep-mpif77
%{_libdir}/openmpi/bin/scorep-mpif90
%{_libdir}/openmpi/bin/scorep-oshcc
%{_libdir}/openmpi/bin/scorep-oshfort
%{_libdir}/openmpi/bin/scorep-score
%{_libdir}/openmpi/bin/scorep-wrapper
%{_libdir}/openmpi/lib/scorep/
%{_includedir}/openmpi-%{_arch}/scorep/

%files openmpi-libs
%{_libdir}/openmpi/lib/*.so*
%endif

%changelog
* Tue May 24 2016 Orion Poplawski <orion@cora.nwra.com> - 2.0.2-1
- Update to 2.0.2

* Fri Apr 15 2016 Orion Poplawski <orion@cora.nwra.com> - 2.0.1-1
- Update to 2.0.1

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
