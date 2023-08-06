#!/bin/osmtKsh
#!/bin/osmtKsh

# HAS NOT BEEN TESTED YET

typeset RcsId="$Id: mmaApachePlusBinsPrep.sh,v 1.1.1.1 2016-06-08 23:49:52 lsipusr Exp $"

if [ "${loadFiles}X" == "X" ] ; then
     seedSubjectBinsPrep.sh  -l $0 "$@"
     exit $?
fi

itemOrderedList=("libApache_mod_ssl" "libApache_mod_ssl_doc")

function item_libApache_mod_ssl {

  mmaThisPkgName="libapache-mod-ssl"
  mmaThisPkgVersion="2.8.9-2.1"
  mmaThisPkgBase=${mmaPkgBase}

  if [ "${opRunOsType}_" == "SunOS_" ] ; then
    mmaPkgSolName=libapache-mod-ssl
    mmaPkgSolVersion=xxx
    mmaThisPkgBinBase=${mmaThisPkgBase}/${opRunOsType}/${opRunMachineArch}
    mmaPkgSelfExtractableFile=""
  elif [ "${opRunOsType}_" == "Linux_" ] ; then
    mmaPkgDebianMethod="apt"
    mmaPkgDebianName="libapache-mod-ssl"
    mmaPkgDebianVersion="2.8.9-2.1"
    mmaThisPkgBinBase=""
    mmaPkgSelfExtractableFile=""
  else
    EH_problem "Unsupported OS ${opRunOsType}"
  fi
}

function item_libApache_mod_ssl_doc {

  mmaThisPkgName="libapache-mod-ssl-doc"
  mmaThisPkgVersion="2.8.9-2.1"
  mmaThisPkgBase=${mmaPkgBase}

  if [ "${opRunOsType}_" == "SunOS_" ] ; then
    mmaPkgSolName=libapache-mod-ssl-doc
    mmaPkgSolVersion=xxx
    mmaThisPkgBinBase=${mmaThisPkgBase}/${opRunOsType}/${opRunMachineArch}
    mmaPkgSelfExtractableFile=""
  elif [ "${opRunOsType}_" == "Linux_" ] ; then
    mmaPkgDebianMethod="apt"
    mmaPkgDebianName="libapache-mod-ssl-doc"
    mmaPkgDebianVersion="2.8.9-2.1"
    mmaThisPkgBinBase=""
    mmaPkgSelfExtractableFile=""
  else
    EH_problem "Unsupported OS ${opRunOsType}"
  fi
}

