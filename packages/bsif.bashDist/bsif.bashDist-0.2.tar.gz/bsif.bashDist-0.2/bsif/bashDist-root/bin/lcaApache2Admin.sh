#!/bin/bash

IimBriefDescription="Apapche2 SysV Daemon Admin"

ORIGIN="
* Revision And Libre-Halaal CopyLeft -- Part Of ByStar -- Best Used With Blee
"

####+BEGIN: bx:dblock:bash:top-of-file :vc "cvs" partof: "bystar" :copyleft "halaal+brief"
typeset RcsId="$Id: lcaApache2Admin.sh,v 1.1.1.1 2016-06-08 23:49:51 lsipusr Exp $"
# *CopyLeft*
# Copyright (c) 2011 Neda Communications, Inc. -- http://www.neda.com
# See PLPC-120001 for restrictions.
# This is a Halaal Poly-Existential intended to remain perpetually Halaal.
####+END:

__author__="
* Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
"


####+BEGIN: bx:dblock:lsip:bash:seed-spec :types "seedAdminDaemonSysV.sh"
SEED="
* /[dblock]/--Seed/: /opt/public/osmt/bin/seedAdminDaemonSysV.sh
"
if [ "${loadFiles}" == "" ] ; then
    /opt/public/osmt/bin/seedAdminDaemonSysV.sh -l $0 "$@" 
    exit $?
fi
####+END:

_CommentBegin_
####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/topControls.org"
*      ================
*  /Controls/:  [[elisp:(org-cycle)][Fold]]  [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[elisp:(bx:org:run-me)][RunMe]] | [[elisp:(delete-other-windows)][(1)]]  | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] 
** /Version Control/:  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]] 

####+END:
_CommentEnd_

_CommentBegin_
*      ================
*      ################ CONTENTS-LIST ################
*      ======[[elisp:(org-cycle)][Fold]]====== *[Current-Info]*  Status, Notes (Tasks/Todo Lists, etc.)
_CommentEnd_

function vis_moduleDescription {  cat  << _EOF_
*      ======[[elisp:(org-cycle)][Fold]]====== *[Related/Xrefs:]*  <<Xref-Here->>  -- External Documents 
**      ====[[elisp:(org-cycle)][Fold]]==== [[file:/libre/ByStar/InitialTemplates/activeDocs/bxServices/versionControl/fullUsagePanel-en.org::Xref-VersionControl][Panel Roadmap Documentation]]
*      ======[[elisp:(org-cycle)][Fold]]====== *[Module Description:]*
    Based on the generic SysV init daemon Start/Stop/Restart.
_EOF_
}

_CommentBegin_
*      ======[[elisp:(org-cycle)][Fold]]====== SysV Daemon Parameter Settings
_CommentEnd_


daemonName="apache2"
daemonControlScript="/etc/init.d/${daemonName}"

serviceDefaultFile="/etc/default/${daemonName}"

# /etc/apache2/
daemonConfigDir="/etc/${daemonName}"
daemonConfigFile="${daemonConfigDir}/${daemonName}.conf"

# /var/log/apache2/
daemonLogDir="/var/log/${daemonName}"
daemonLogFile="${daemonLogDir}/access.log"
daemonLogErrFile="${daemonLogDir}/error.log"


_CommentBegin_
*      ======[[elisp:(org-cycle)][Fold]]====== Examples
_CommentEnd_


function vis_examples {
  typeset extraInfo="-h -v -n showRun"
  #typeset extraInfo=""

#$( examplesSeperatorSection "Section Title" )

  visLibExamplesOutput ${G_myName} 
  cat  << _EOF_
$( examplesSeperatorTopLabel "${G_myName}" )
_EOF_

  vis_examplesFullService
  vis_examplesDaemonControl


  cat  << _EOF_
$( examplesSeperatorChapter "Server Config" )
$( examplesSeperatorChapter "Server Config -- Modules" )
${G_myName} ${extraInfo} -i apache2ModsEnable
a2enmod
a2dismod
$( examplesSeperatorChapter "Server Config -- Ports" )
${G_myName} ${extraInfo} -i apache2PortsStdout
${G_myName} ${extraInfo} -i apache2PortsUpdate
$( examplesSeperatorChapter "Server Config -- Global Configs" )
a2enconf
a2disconf
$( examplesSeperatorChapter "Server Config -- Sites" )
a2ensite gitweb.example.com.conf
a2dissite gitweb.example.com.conf
_EOF_

  
  vis_examplesServerConfig

  vis_examplesLogInfo

 cat  << _EOF_
$( examplesSeperatorChapter "Validation and Testing" )
apache2ctl -S             # Configuration Description
apachectl configtest      # Syntax Check/Verification
a2query -v                # Apache2 Version
a2query -a                # Apache2 Modules Version
telnet localhost 80
openssl s_client -connect localhost:443 -state -debug
curl http://localhost/
curl https://localhost/
_EOF_
}

noArgsHook() {
  vis_examples
}

_CommentBegin_
*      ======[[elisp:(org-cycle)][Fold]]====== Server Config Overwrites
_CommentEnd_


#
# NOTE WELL: vis_serverConfigUpdate overwrites the seed
#

function vis_serverConfigUpdate {
    # seed Overwrite

    opDo vis_apache2PortsUpdate
    opDo vis_apache2ModsEnable
}


_CommentBegin_
*      ======[[elisp:(org-cycle)][Fold]]====== Server Config -- Enable Modules
_CommentEnd_



function vis_apache2ModsEnable {
    G_funcEntry
    function describeF {  G_funcEntryShow; cat  << _EOF_
    #opDo apt-get -y install libapache2-mod-proxy-html
_EOF_
    }
    EH_assert [[ $# -eq 0 ]]

    if vis_reRunAsRoot ${G_thisFunc} $@ ; then lpReturn ${globalReRunRetVal}; fi;

    opDo a2enmod proxy
    opDo a2enmod proxy_html
    opDo a2enmod proxy_http
    opDo a2enmod xml2enc
    opDo a2enmod proxy_balancer
    opDo a2enmod headers
    opDo a2enmod rewrite
    opDo a2enmod actions
    opDo a2enmod wsgi
    opDo a2enmod suexec
    opDo a2enmod rewrite
    opDo a2enmod cgi

    #
    # SSL 
    #
    opDo a2ensite default-ssl
    opDo a2enmod ssl

    opDo /etc/init.d/apache2 restart
}


_CommentBegin_
*      ======[[elisp:(org-cycle)][Fold]]====== Server Config -- Ports Update
_CommentEnd_



function vis_apache2PortsStdout {
    G_funcEntry
    function describeF {  G_funcEntryShow; cat  << _EOF_
_EOF_
    }
    EH_assert [[ $# -eq 0 ]]

  cat  << _EOF_
# Generated by ${G_myName}:${G_thisFunc} on ${dateTag} -- Do Not Hand Edit
#
# If you just change the port or add more ports here, you will likely also
# have to change the VirtualHost statement in
# /etc/apache2/sites-enabled/000-default.conf

Listen 80

<IfModule ssl_module>
	Listen 443
</IfModule>

<IfModule mod_gnutls.c>
	Listen 443
</IfModule>

_EOF_
}


function vis_apache2PortsUpdate {
    G_funcEntry
    function describeF {  G_funcEntryShow; cat  << _EOF_
_EOF_
    }
    EH_assert [[ $# -eq 0 ]]

    if vis_reRunAsRoot ${G_thisFunc} $@ ; then lpReturn ${globalReRunRetVal}; fi;
  
    typeset thisConfigFile="/etc/apache2/ports.conf"

    FN_fileSafeKeep ${thisConfigFile}

    opDo eval vis_apache2PortsStdout '>' ${thisConfigFile}

    opDo ls -l ${thisConfigFile}

    opDo /etc/init.d/apache2 force-reload
}


_CommentBegin_
*      ======[[elisp:(org-cycle)][Fold]]====== Obsoleted
_CommentEnd_


function vis_apache2PortsStdoutObsoleted {

  opDoExit opNetCfg_paramsGet ${opRunClusterName} ${opRunHostName}
    # ${opNetCfg_ipAddr} ${opNetCfg_netmask} ${opNetCfg_networkAddr} ${opNetCfg_defaultRoute}

  #thisIPAddress=`lpL3Hosts.sh -p clusterName=${opRunClusterName} -p hostName=${opRunHostName} -i givenHostGetIPaddr`    
  opDo lpParamsBasicGet
  
  thisIPAddress=${lpDnsEntryIpAddr}


  cat  << _EOF_
# If you just change the port or add more ports here, you will likely also
# have to change the VirtualHost statement in
# /etc/apache2/sites-enabled/000-default
# This is also true if you have upgraded from before 2.2.9-3 (i.e. from
# Debian etch). See /usr/share/doc/apache2.2-common/NEWS.Debian.gz and
# README.Debian.gz
#
# Generated by ${G_myName} on ${dateTag}

NameVirtualHost ${thisIPAddress}
Listen 80

<IfModule mod_ssl.c>
    # SSL name based virtual hosts are not yet supported, therefore no
    # NameVirtualHost statement here
    Listen 443
</IfModule>
_EOF_
}


####+BEGIN: bx:dblock:bash:end-of-file :type "basic"
_CommentBegin_
*      ================ /[dblock] -- End-Of-File Controls/
_CommentEnd_
#+STARTUP: showall
#local variables:
#major-mode: sh-mode
#fill-column: 90
# end:
####+END:
