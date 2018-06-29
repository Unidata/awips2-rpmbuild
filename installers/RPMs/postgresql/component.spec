%define _build_arch %(uname -i)
%define _postgresql_version 9.5.13
%define _postgres_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _postgres_src_loc %{_baseline_workspace}/foss/postgresql
%define _postgres_script_loc %{_baseline_workspace}/installers/RPMs/postgresql/scripts
%define _gdal 2.2.4
%define _geos 3.6.2
%define _postgis 2.4.4
%define _proj 5.1.0
#
# AWIPS II PostgreSQL Spec File
#

Name: awips2-postgresql
Summary: AWIPS II PostgreSQL Distribution
Version: %{_postgresql_version}
Release: %{_component_version}.%{_component_release}%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
BuildRequires: openssl-devel >= 1.0.1e
Requires: openssl >= 1.0.1e
Requires: netcdf
provides: awips2-postgresql
provides: awips2-base-component

%description
AWIPS II PostgreSQL Distribution - Contains the AWIPS II PostgreSQL Distribution.
This is just the postgresql application. There is a separate rpm that will initialize
and populate the AWIPS II databases.

%prep
# Ensure that a "buildroot" has been specified.
if [ "%{_build_root}" = "" ]; then
   echo "ERROR: A BuildRoot has not been specified."
   echo "FATAL: Unable to Continue ... Terminating."
   exit 1
fi

if [ -d %{_build_root} ]; then
   rm -rf %{_build_root}
fi
/bin/mkdir -p %{_build_root}
if [ $? -ne 0 ]; then
   exit 1
fi
if [ -d %{_postgres_build_loc} ]; then
   rm -rf %{_postgres_build_loc}
fi
mkdir -p %{_postgres_build_loc}
if [ $? -ne 0 ]; then
   exit 1
fi
mkdir -p %{_postgres_build_loc}/awips2/postgresql
if [ $? -ne 0 ]; then
   exit 1
fi

SRC_DIR="%{_postgres_src_loc}/packaged"
POSTGRESQL_TAR_FILE="postgresql-%{_postgresql_version}.tar.gz"

# Copy our source tar file to the build directory.
cp ${SRC_DIR}/${POSTGRESQL_TAR_FILE} %{_postgres_build_loc}

# Untar the postgresql source
cd %{_postgres_build_loc}

tar -xvf ${POSTGRESQL_TAR_FILE}

%build
cd %{_postgres_build_loc}/postgresql-%{_postgresql_version}

LDFLAGS='-Wl,-rpath,/awips2/postgresql/lib,-rpath,/awips2/psql/lib' ./configure \
   --prefix=%{_postgres_build_loc}/awips2/postgresql \
   --with-openssl \
   --with-libxml
if [ $? -ne 0 ]; then
   exit 1
fi
make clean
if [ $? -ne 0 ]; then
   exit 1
fi

make %{?_smp_mflags}
if [ $? -ne 0 ]; then
   exit 1
fi

cd %{_postgres_build_loc}/postgresql-%{_postgresql_version}/contrib/pg_freespacemap
make
if [ $? -ne 0 ]; then
   exit 1
fi

cd %{_postgres_build_loc}/postgresql-%{_postgresql_version}/contrib/xml2
make %{?_smp_mflags}
if [ $? -ne 0 ]; then
   exit 1
fi

%install
# Copies the standard Raytheon licenses into a license directory for the
# current component.
function copyLegal()
{
   # $1 == Component Build Root
   
   COMPONENT_BUILD_DIR=${1}
   
   mkdir -p ${RPM_BUILD_ROOT}/${COMPONENT_BUILD_DIR}/licenses
   
   # Create a Tar file with our FOSS licenses.
   tar -cjf %{_baseline_workspace}/rpms/legal/FOSS_licenses.tar \
      %{_baseline_workspace}/rpms/legal/FOSS_licenses/
   
   cp "%{_baseline_workspace}/rpms/legal/Master_Rights_File.pdf" \
      ${RPM_BUILD_ROOT}/${COMPONENT_BUILD_DIR}/licenses
   cp %{_baseline_workspace}/rpms/legal/FOSS_licenses.tar \
      ${RPM_BUILD_ROOT}/${COMPONENT_BUILD_DIR}/licenses
      
   rm -f %{_baseline_workspace}/rpms/legal/FOSS_licenses.tar    
}

mkdir -p %{_build_root}/awips2/postgresql
mkdir -p %{_build_root}/awips2/psql

cd %{_postgres_build_loc}/postgresql-%{_postgresql_version}

make install
if [ $? -ne 0 ]; then
   exit 1
fi

cd %{_postgres_build_loc}/postgresql-%{_postgresql_version}/contrib/xml2

make install
if [ $? -ne 0 ]; then
   exit 1
fi

# relocate the psql executable
mkdir -p %{_build_root}/awips2/psql/bin
mv -v %{_postgres_build_loc}/awips2/postgresql/bin/psql \
   %{_build_root}/awips2/psql/bin/psql
if [ $? -ne 0 ]; then
   exit 1
fi
# duplicate libpq; eventually, we should just have PostgreSQL
# reference the libpq in /awips2/psq/lib
mkdir -p %{_build_root}/awips2/psql/lib
cp -Pv %{_postgres_build_loc}/awips2/postgresql/lib/libpq.so* \
   %{_build_root}/awips2/psql/lib
if [ $? -ne 0 ]; then
   exit 1
fi

SRC_DIR="%{_postgres_src_loc}/packaged"
PROJ_SRC="proj-%{_proj}.tar.gz"
POSTGIS_SRC="postgis-%{_postgis}.tar.gz"
GEOS_BASE="geos-"%{_geos}
GEOS_SRC="geos-%{_geos}.tar.bz2"
GDAL_SRC="gdal-%{_gdal}.tar.gz"
POSTGIS_OLD_SRC="postgis-2.0.6.tar.gz"

# The directory that the src will be in after the tars are unzipped.
PROJ_SRC_DIR="proj-%{_proj}"
POSTGIS_SRC_DIR="postgis-%{_postgis}"
GEOS_SRC_DIR="geos-%{_geos}"
GDAL_SRC_DIR="gdal-%{_gdal}"
POSTGIS_OLD_SRC_DIR="postgis-2.0.6"

cp ${SRC_DIR}/${POSTGIS_SRC} %{_postgres_build_loc}
cp ${SRC_DIR}/${PROJ_SRC} %{_postgres_build_loc}
cp %{_baseline_workspace}/foss/geos/${GEOS_SRC} %{_postgres_build_loc}
cp ${SRC_DIR}/${GDAL_SRC} %{_postgres_build_loc}
cp ${SRC_DIR}/${POSTGIS_OLD_SRC} %{_postgres_build_loc}

cd %{_postgres_build_loc}
tar -xvzf ${PROJ_SRC}
if [ $? -ne 0 ]; then
   exit 1
fi

tar -xvf ${POSTGIS_SRC}
if [ $? -ne 0 ]; then
   exit 1
fi

tar -xvf ${POSTGIS_OLD_SRC}
if [ $? -ne 0 ]; then
   exit 1
fi
# Patch required for PostGIS 2.0.6 to compile with PostgreSQL 9.5.x
/usr/bin/patch -p1 -i "${SRC_DIR}"/postgis-2.0.6-build-fix.patch
if [ $? -ne 0 ]; then
   exit 1
fi

tar -xvf ${GEOS_SRC}
if [ $? -ne 0 ]; then
   exit 1
fi
tar -xvzf ${GDAL_SRC}
if [ $? -ne 0 ]; then
   exit 1
fi

pushd ${GEOS_SRC_DIR}
LDFLAGS='-Wl,-rpath,/awips2/postgresql/lib,-rpath,/awips2/psql/lib' ./configure \
   --prefix=%{_postgres_build_loc}/awips2/postgresql
if [ $? -ne 0 ]; then
   exit 1
fi
make %{?_smp_mflags}
if [ $? -ne 0 ]; then
   exit 1
fi
make install
if [ $? -ne 0 ]; then
   exit 1
fi
popd

pushd ${PROJ_SRC_DIR}
LDFLAGS='-Wl,-rpath,/awips2/postgresql/lib,-rpath,/awips2/psql/lib' ./configure \
   --prefix=%{_postgres_build_loc}/awips2/postgresql \
   --without-jni
if [ $? -ne 0 ]; then
   exit 1
fi
make %{?_smp_mflags}
if [ $? -ne 0 ]; then
   exit 1
fi
make install
if [ $? -ne 0 ]; then
   exit 1
fi
popd

pushd ${GDAL_SRC_DIR}
LDFLAGS='-Wl,-rpath,/awips2/postgresql/lib,-rpath,/awips2/psql/lib' ./configure \
   --prefix=%{_postgres_build_loc}/awips2/postgresql \
   --with-expat-lib=%{_usr}/%{_lib}
if [ $? -ne 0 ]; then
   exit 1
fi
make %{?_smp_mflags}
if [ $? -ne 0 ]; then
   exit 1
fi
make install
if [ $? -ne 0 ]; then
   exit 1
fi
popd

pushd ${POSTGIS_SRC_DIR}
_POSTGRESQL_ROOT=%{_postgres_build_loc}/awips2/postgresql
_POSTGRESQL_BIN=${_POSTGRESQL_ROOT}/bin
LDFLAGS='-Wl,-rpath,/awips2/postgresql/lib,-rpath,/awips2/psql/lib' ./configure \
    --with-pgconfig=${_POSTGRESQL_BIN}/pg_config \
    --with-geosconfig=${_POSTGRESQL_BIN}/geos-config \
    --with-projdir=${_POSTGRESQL_ROOT} \
    --with-gdalconfig=${_POSTGRESQL_BIN}/gdal-config \
    --prefix=%{_postgres_build_loc}/awips2/postgresql
if [ $? -ne 0 ]; then
    exit 1
fi
# disable doc since it attempts to download files from
# the internet
echo "#Do Nothing" > doc/Makefile.in
echo "docs:" > doc/Makefile
echo "" >> doc/Makefile
echo "docs-install:" >> doc/Makefile
echo "" >> doc/Makefile
echo "docs-uninstall:" >> doc/Makefile
echo "" >> doc/Makefile
echo "comments-install:" >> doc/Makefile
echo "" >> doc/Makefile
echo "comments-uninstall:" >> doc/Makefile
echo "" >> doc/Makefile
echo "clean:" >> doc/Makefile
echo "" >> doc/Makefile
echo "all:" >> doc/Makefile
echo "" >> doc/Makefile
echo "install:" >> doc/Makefile
echo "" >> doc/Makefile
make
# run make twice - the first time may fail due to doc
make
if [ $? -ne 0 ]; then
    exit 1
fi
make install
if [ $? -ne 0 ]; then
    exit 1
fi

# Create The PostgreSQL Data Directory
mkdir -p ${RPM_BUILD_ROOT}/awips2/database/data

/bin/cp -Rf %{_postgres_build_loc}/awips2/postgresql/* %{_build_root}/awips2/postgresql
if [ $? -ne 0 ]; then
   exit 1
fi

# Copy The Startup Script
cp -r %{_postgres_script_loc}/start_postgres.sh ${RPM_BUILD_ROOT}/awips2/postgresql/bin

copyLegal "awips2/postgresql"

mkdir -p %{_build_root}/etc/init.d

# Include the postgresql service script
cp %{_postgres_script_loc}/init.d/edex_postgres \
   %{_build_root}/etc/init.d

%preun
if [ "${1}" = "1" ]; then
   exit 0
fi
if [ -f /etc/init.d/edex_postgres ]; then
   /sbin/chkconfig --del edex_postgres
fi

%clean
rm -rf ${RPM_BUILD_ROOT}
rm -rf %{_postgres_build_loc}

%package -n awips2-psql

Summary: AWIPS II PSQL Distribution
Group: AWIPSII

provides: awips2-psql

%description -n awips2-psql
AWIPS II PSQL Distribution - Contains the AWIPS II PSQL Distribution.
This is just the postgresql application. There is a separate rpm that will initialize
and populate the AWIPS II databases.

%files
%defattr(644,awips,fxalpha,755)
%attr(744,root,root) /etc/init.d/edex_postgres
%attr(700,awips,fxalpha) /awips2/database/data
%dir /awips2/postgresql
%dir /awips2/postgresql/include
/awips2/postgresql/include/*
%dir /awips2/postgresql/lib
/awips2/postgresql/lib/*
%docdir /awips2/postgresql/licenses
%dir /awips2/postgresql/licenses
/awips2/postgresql/licenses/*
%dir /awips2/postgresql/share
/awips2/postgresql/share/*

%defattr(755,awips,fxalpha,755)
%dir /awips2/postgresql/bin
/awips2/postgresql/bin/*

%files -n awips2-psql
%defattr(755,awips,fxalpha,755)
%dir /awips2/psql
%dir /awips2/psql/bin
/awips2/psql/bin/*

%defattr(644,awips,fxalpha,755)
%dir /awips2/psql/lib
/awips2/psql/lib/*
