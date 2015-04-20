%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%define _build_arch %(uname -i)
%define _python_pkgs_dir "%{_baseline_workspace}/pythonPackages"
%define _python_build_loc %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#
# AWIPS II Python scipy Spec File
#
Name: awips2-python-scipy
Summary: AWIPS II Python scipy Distribution
Version: 0.15.0
Release: %{_component_version}.%{_component_release}%{?dist}
Group: AWIPSII
BuildRoot: %{_build_root}
BuildArch: %{_build_arch}
URL: N/A
License: N/A
Distribution: N/A
Vendor: Raytheon
Packager: Bryan Kowal

AutoReq: no
requires: awips2-python
requires: awips2-python-numpy
provides: awips2-python-scipy

%description
AWIPS II Python scipy Site-Package

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

%build
SCIPY_SRC_DIR="%{_baseline_workspace}/foss/scipy-%{version}/packaged"

cp -v ${SCIPY_SRC_DIR}/* \
   %{_python_build_loc}
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

export BLAS=/awips2/python/lib
export LAPACK=/awips2/python/lib
source /etc/profile.d/awips2Python.sh
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi

pushd . > /dev/null
cd %{_python_build_loc}
tar xvf scipy-%{version}.tar.gz
cd scipy-%{version}
export LD_LIBRARY_PATH=/awips2/python/lib
/awips2/python/bin/python setup.py build
RC=$?
if [ ${RC} -ne 0 ]; then
   # Try to build a second time. It seems to work
   # for some reason.
   /awips2/python/bin/python setup.py build
   RC=$?
   if [ ${RC} -ne 0 ]; then
      exit 1
   fi
fi
popd > /dev/null

%install

export BLAS=/awips2/python/lib
export LAPACK=/awips2/python/lib

pushd . > /dev/null
cd %{_python_build_loc}/scipy-%{version}
export LD_LIBRARY_PATH=/awips2/python/lib
/awips2/python/bin/python setup.py install \
   --root=%{_build_root} \
   --prefix=/awips2/python
RC=$?
if [ ${RC} -ne 0 ]; then
   exit 1
fi
popd > /dev/null

%clean
rm -rf %{_build_root}
rm -rf %{_python_build_loc}

%files
%defattr(644,awips,fxalpha,755)
%dir /awips2/python/lib/python2.7/site-packages
/awips2/python/lib/python2.7/site-packages/*
