#!/bin/osmtKsh
#!/bin/osmtKsh 

typeset RcsId="$Id: mmaApacheBinsPrep.sh,v 1.1.1.1 2016-06-08 23:49:51 lsipusr Exp $"

if [ "${loadFiles}X" == "X" ] ; then
    seedActions.sh -l $0 "$@"
    exit $?
fi

if [ "${opRunOsType}_" == "SunOS_" ] ; then
  if [[ "${opRunOsRev}_" == "5.7_" ]] ; then
    mmaThisPkgName="SMCapache"
    mmaThisPkgVersion=1.3.6
    # /opt/public/mmaPkgs/apache-1.3.6/SunOS/sol7.sun4m/apache-1.3.6-sol7-sparc-local 
    mmaThisPkgBase=${mmaPkgBase}/apache-1.3.6
    mmaPkgSolName="SMCapache"
    mmaPkgSolVersion="1.3.6"

    mmaThisPkgBinBase=${mmaThisPkgBase}/${opRunOsType}/sol7.${opRunMachineArch}
    mmaPkgSolFile=${mmaThisPkgBinBase}/apache-1.3.6-sol7-sparc-local
  elif [[ "${opRunOsRev}_" == "5.8_" ]] ; then
    mmaThisPkgName="SMCapache"
    mmaThisPkgVersion=1.3.12
    # /opt/public/mmaPkgs/apache-1.3.12/SunOS/sol8.sun4m/apache-1.3.12-sol8-sparc-local 
    mmaThisPkgBase=${mmaPkgBase}/apache-1.3.12
    mmaPkgSolName="SMCapache"
    mmaPkgSolVersion="1.3.12"
    mmaThisPkgBinBase=${mmaThisPkgBase}/${opRunOsType}/sol8.${opRunMachineArch}
    mmaPkgSolFile=${mmaThisPkgBinBase}/apache-1.3.12-sol8-sparc-local
  else
    EH_problem "Unsupported OS Rev: ${opRunOsRev}"
    return 1
  fi
elif [ "${opRunOsType}_" == "Linux_" ] ; then
  mmaThisPkgName="apache"
  mmaThisPkgVersion=1.3.23-1
  # /opt/public/mmaPkgs/apache-1.3.12/SunOS/sol8.sun4m/apache-1.3.12-sol8-sparc-local 
  mmaThisPkgBase=${mmaPkgBase}/apache-1.3.12

  mmaPkgDebianName="apache"
  mmaPkgDebianVersion="1.3.23-1"
  mmaThisPkgBinBase=${mmaThisPkgBase}/${opRunOsType}
  mmaPkgDebianFile=${mmaThisPkgBinBase}
else
  EH_problem "Unsupported OS ${opRunOsType}"
fi

. ${opBinBase}/mmaLib.sh
. ${opBinBase}/mmaBinsPrepLib.sh

function vis_examples {
  typeset visLibExamples=`visLibExamplesOutput ${G_myName}`
 cat  << _EOF_
EXAMPLES:
${visLibExamples}
--- OBTAIN SRC/PKG ---
${G_myName} -i obtain
${G_myName} -i srcUnpack
--- GENERATE BINARIES FROM SOURCES ---
${G_myName} -i srcBuild
${G_myName} -i srcClean
${G_myName} -i srcBuildAndInstall
--- GENERATE PACKAGE ---
${G_myName} -i pkgMake
--- COMPONENT MANIPULATORS  ---
${G_myName} -i compVerify
${G_myName} -i compUpdate
${G_myName} -i compDelete
--- COMPONENT ACTIVATION ---
${G_myName} -i compInitInstall
--- FULL SERVICE ---
${G_myName} -i fullVerify
${G_myName} -i fullUpdate
--- INFORMATION ---
${G_myName} -i compInfo
${G_myName} -i pkgInfo
_EOF_
}


function vis_help {
  cat  << _EOF_
_EOF_
}

function noArgsHook {
    vis_examples
}

# System
function vis_compInfo {
  mmaCompAuto_info
}

# Pkg
function vis_pkgInfo {
  mmaPkgAuto_info
}

function vis_obtain {
  mmaPkgAuto_obtain
}

function vis_compVerify {
  mmaCompAuto_verify
  vis_checkForDependent
}

function vis_compUpdate {
  mmaCompAuto_update
  vis_checkForDependent update
}

function vis_compDelete {
  mmaCompAuto_delete
}

function vis_fullVerify {
  vis_compVerify
}

function vis_fullUpdate {
  vis_compUpdate
  opDo mmaApachePlusBinsPrep.sh -s all -a fullUpdate
  
  #opDo tomcatPortalDomains.sh -i  makeCertificate
  
  #opDoComplain mmaWebServers.sh -p baseSet=devenv -s webSrv_${opRunHostName} -a fullUpdate
  #vis_compInitInstall
}

function vis_checkForDependent {
  EH_assert [[ "${opRunOsType}_" == "Linux_" ]]
  
  dependentLists=("libwww_perl" "libmime_base64_perl" "liburi_perl" "libdevel_symdump_perl" "libapache_mod_perl")

  function libwww_perl {
    mmaPkgDebianName=libwww-perl
    mmaPkgDebianVersion=5.64-1
    # /v1/opt/public/mmaPkgs/libwww-perl-5.64/Linux/i686/libwww-perl_5.64-1_all.deb 
    mmaPkgDebianFile=/opt/public/mmaPkgs/${mmaPkgDebianName}-5.64/${opRunOsType}/${opRunMachineArch}/libwww-perl_5.64-1_all.deb
  }

  function libmime_base64_perl {
    mmaPkgDebianName=libmime-base64-perl
    mmaPkgDebianVersion=2.12-4
    # /v1/opt/public/mmaPkgs/libmime-base64-perl-2.12/Linux/i686/libmime-base64-perl_2.12-4_i386.deb 
    mmaPkgDebianFile=/opt/public/mmaPkgs/${mmaPkgDebianName}-2.12/${opRunOsType}/${opRunMachineArch}/libmime-base64-perl_2.12-4_i386.deb
  }

  function liburi_perl {
    mmaPkgDebianName=liburi-perl
    mmaPkgDebianVersion=1.18-1
    # /v1/opt/public/mmaPkgs/liburi-perl-1.18/Linux/i686/liburi-perl_1.18-1_all.deb 
    mmaPkgDebianFile=/opt/public/mmaPkgs/${mmaPkgDebianName}-1.18/${opRunOsType}/${opRunMachineArch}/liburi-perl_1.18-1_all.deb
  }

  function libdevel_symdump_perl {
    mmaPkgDebianName=libdevel-symdump-perl
    mmaPkgDebianVersion=2.03-1
    # /v1/opt/public/mmaPkgs/libdevel-symdump-perl-2.03/Linux/i686/libdevel-symdump-perl_2.03-1_all.deb 
    mmaPkgDebianFile=/opt/public/mmaPkgs/${mmaPkgDebianName}-2.03/${opRunOsType}/${opRunMachineArch}/libdevel-symdump-perl_2.03-1_all.deb
  }

  function libapache_mod_perl {
    mmaPkgDebianName=libapache-mod-perl
    mmaPkgDebianVersion=1.26-4
    # /v1/opt/public/mmaPkgs/libapache-mod-perl-1.26/Linux/i686/libapache-mod-perl_1.26-4_i386.deb 
    mmaPkgDebianFile=/opt/public/mmaPkgs/${mmaPkgDebianName}-1.26/${opRunOsType}/${opRunMachineArch}/libapache-mod-perl_1.26-4_i386.deb
  }

  print "Check for dependent ...."

  typeset oneComp
  for oneComp in ${dependentLists[@]} ; do
    ${oneComp}
    mmaCompDebian_verify ${mmaPkgDebianName} ${mmaPkgDebianVersion}
    if [[ "$1_" == "update_" ]] ; then
      mmaCompDebian_update ${mmaPkgDebianName} ${mmaPkgDebianVersion} ${mmaPkgDebianFile}
    fi
  done
}

