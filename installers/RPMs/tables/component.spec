%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%define _hdf5_version 1.8.4

#
# AWIPS II Python tables Spec File
#
Name: awips2-python-tables
Summary: AWIPS II Python tables Distribution
Version: 3.1.0
Release: 1%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: %{_build_vendor}
Packager: %{_build_site}

AutoReq: no
Requires: awips2-python
Requires: awips2-python-numpy
Provides: awips2-python-tables = %{version}

BuildRequires: awips2-python
BuildRequires: awips2-python-numpy

%description
AWIPS II Python tables Site-Package - 64-bit.

%prep
# Verify That The User Has Specified A BuildRoot.
if [ "%{_build_root}" = "" ]
then
   echo "A Build Root has not been specified."
   echo "Unable To Continue ... Terminating"
   exit 1
fi

rm -rf %{_build_root}
mkdir -p %{_build_root}
if [ -d %{_python_build_loc} ]; then
   rm -rf %{_python_build_loc}
fi
mkdir -p %{_python_build_loc}

PRE_REQS_HDF5_TAR=""
if [ "%{_build_arch}" = "i386" ]; then
   PRE_REQS_HDF5_TAR="hdf5-%{_hdf5_version}-patch1-linux-shared.tar.gz"
else
   if [ "%{_build_arch}" = "x86_64" ]; then
      PRE_REQS_HDF5_TAR="hdf5-%{_hdf5_version}-patch1-linux-x86_64-shared.tar.gz"
   else
      echo "ERROR: Unrecognized Architecture."
      exit 1
   fi
fi

PRE_REQS_DIR="%{_baseline_workspace}/rpms/python.site-packages/deploy.builder/pre-reqs"
cp -v ${PRE_REQS_DIR}/${PRE_REQS_HDF5_TAR} \
   %{_python_build_loc}/
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null
cd %{_python_build_loc}
/bin/tar -xvf ${PRE_REQS_HDF5_TAR}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
rm -f ${PRE_REQS_HDF5_TAR}
popd > /dev/null

%build
export HDF5_DIR=
if [ "%{_build_arch}" = "i386" ]; then
   export HDF5_DIR="%{_python_build_loc}/hdf5-%{_hdf5_version}-patch1-linux-shared"
else
   export HDF5_DIR="%{_python_build_loc}/hdf5-%{_hdf5_version}-patch1-linux-x86_64-shared"
fi

TABLES_SRC_DIR="%{_baseline_workspace}/foss/tables/packaged"
TABLES_TAR="v.%{version}.tar.gz"
TABLES_DIR="PyTables-v.%{version}"
cp -R ${TABLES_SRC_DIR}/${TABLES_TAR} \
   %{_python_build_loc}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

cd %{_python_build_loc}
tar -xvzf ${TABLES_TAR}

pushd . > /dev/null
cd %{_python_build_loc}/${TABLES_DIR}
cp ${TABLES_SRC_DIR}/setup.py .
/awips2/python/bin/python setup.py build_ext --inplace
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%install
TABLES_DIR="PyTables-v.%{version}"
export HDF5_DIR=
if [ "%{_build_arch}" = "i386" ]; then
   export HDF5_DIR="%{_python_build_loc}/hdf5-%{_hdf5_version}-patch1-linux-shared"
else
   export HDF5_DIR="%{_python_build_loc}/hdf5-%{_hdf5_version}-patch1-linux-x86_64-shared"
fi

pushd . > /dev/null
cd %{_python_build_loc}/${TABLES_DIR}
/awips2/python/bin/python setup.py install \
   --root=%{_build_root} \
   --prefix=/awips2/python
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%pre

%post

%preun

%postun

%clean
rm -rf %{_build_root}
rm -rf %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
%dir /awips2/python/lib/python2.7/site-packages
/awips2/python/lib/python2.7/site-packages/*
%defattr(755,awips,fxalpha,755)
%dir /awips2/python/bin
/awips2/python/bin/*
