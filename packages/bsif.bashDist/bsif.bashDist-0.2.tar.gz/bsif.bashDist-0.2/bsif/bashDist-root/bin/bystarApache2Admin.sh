#!/bin/osmtKsh
#!/bin/osmtKsh 

typeset RcsId="$Id: bystarApache2Admin.sh,v 1.1.1.1 2016-06-08 23:49:51 lsipusr Exp $"

if [ "${loadFiles}X" == "X" ] ; then
    seedActions.sh -l $0 "$@"
    exit $?
fi


vis_help () {
  cat  << _EOF_


_EOF_
}

. ${opBinBase}/bystarHook.libSh

# bystarLib.sh
. ${opBinBase}/bystarLib.sh
. ${opBinBase}/bynameLib.sh
. ${opBinBase}/mmaLib.sh
. ${opBinBase}/mmaQmailLib.sh
. ${opBinBase}/mmaDnsLib.sh

. ${opBinBase}/opAcctLib.sh

. ${opBinBase}/lpCurrents.libSh

. ${opBinBase}/lpParams.libSh

# PRE parameters
typeset -t acctTypePrefix=""
typeset -t bystarUid="MANDATORY"

function G_postParamHook {
    bystarUidHome=$( FN_absolutePathGet ~${bystarUid} )
    lpCurrentsGet
}


function vis_examples {
  typeset extraInfo="-h -v -n showRun"
  #typeset extraInfo=""
  # NOTYET, outofdate
  typeset doLibExamples=`doLibExamplesOutput ${G_myName}`

  typeset thisAcctTypePrefix="sa"
  #typeset thisOneSaNu="sa-20051"
  #typeset thisOneSaNu=${oneBystarAcct}
  typeset thisOneSaNu=${currentBystarUid}
  typeset oneSubject="qmailAddr_test"
 cat  << _EOF_
EXAMPLES:
${doLibExamples}
--- PROVISIONING ACTIONS ---
${G_myName} ${extraInfo} -p bystarUid=${thisOneSaNu} -i  fullUpdate
${G_myName} ${extraInfo} -p bystarUid=${thisOneSaNu} -f -i  fullUpdate
--- Base Account Prep ---
${G_myName} ${extraInfo} -p bystarUid=${thisOneSaNu} -i  apache2SiteBasePrep
--- Virtual Host Account CONFIG (web.xxx) ---
${G_myName} ${extraInfo} -p bystarUid=${thisOneSaNu} -i  virHostSiteConfigStdout
${G_myName} ${extraInfo} -p bystarUid=${thisOneSaNu} -i  virHostSiteConfigUpdate
${G_myName} ${extraInfo} -p bystarUid=${thisOneSaNu} -i  virHostSiteConfigVerify
${G_myName} ${extraInfo} -p bystarUid=${thisOneSaNu} -i  virHostSiteConfigShow
${G_myName} ${extraInfo} -p bystarUid=${thisOneSaNu} -i  virHostSiteConfigDelete
${G_myName} ${extraInfo} -p bystarUid=${thisOneSaNu} -i  virHostSiteConfigEnable
${G_myName} ${extraInfo} -p bystarUid=${thisOneSaNu} -i  virHostSiteConfigDisable
--- 
${G_myName} ${extraInfo} -i a2ensite  siteName
${G_myName} ${extraInfo} -i a2dissite siteName
--- DNS ---
${G_myName} ${extraInfo} -p bystarUid=${thisOneSaNu} -i dnsUpdate
${G_myName} ${extraInfo} -p bystarUid=${thisOneSaNu} -i  dnsDelete
--- DEACTIVATION ACTIONS ---
${G_myName} ${extraInfo} -p bystarUid=${thisOneSaNu} -i  fullDelete
${G_myName} ${extraInfo} -p bystarUid=${thisOneSaNu} -i  serviceDelete
_EOF_
}

noArgsHook() {
  vis_examples
}

noSubjectHook() {
  return 0
}



function vis_fullUpdate {
    EH_assert [[ $# -eq 0 ]]
    EH_assert [[ "${bystarUid}_" != "MANDATORY_" ]]

    bystarBagpLoad

    opDoComplain vis_dnsUpdate

    opDoComplain vis_fullEssentials

    opDoComplain vis_fullSupplements

}


function vis_fullSupplements {
    EH_assert [[ $# -eq 0 ]]
    EH_assert [[ "${bystarUid}_" != "MANDATORY_" ]]
    return
}

function vis_fullEssentials {
    EH_assert [[ $# -eq 0 ]]
    EH_assert [[ "${bystarUid}_" != "MANDATORY_" ]]

    bystarBagpLoad

    opDo vis_apache2SiteBasePrep

    opDo vis_virHostSiteConfigUpdate
}


function vis_fullDelete {
    G_funcEntry
    function describeF {  G_funcEntryShow; cat  << _EOF_
_EOF_
    }
    EH_assert [[ $# -eq 0 ]]

    opDo vis_serviceDelete

    opDoComplain vis_dnsDelete

    lpReturn
}



function vis_apache2SiteBasePrep {
    EH_assert [[ $# -eq 0 ]]
    EH_assert [[ "${bystarUid}_" != "MANDATORY_" ]]

  G_abortIfNotRunningAsRoot

  opDoRet bystarAcctAnalyze ${bystarUid}

  opAcctInfoGet ${bystarUid}

  #FN_dirSafeKeep ${opAcct_homeDir}/lcaApache2

  opDoExit mkdir -p ${opAcct_homeDir}/lcaApache2
  opDoExit mkdir -p ${opAcct_homeDir}/lcaApache2/web/htdocs
  opDoExit mkdir -p ${opAcct_homeDir}/lcaApache2/web/logs

  # OBSOLETED -- moved to bystarPlone3Admin.sh 
  #opDoExit mkdir -p ${opAcct_homeDir}/lcaApache2/www/htdocs
  #opDoExit mkdir -p ${opAcct_homeDir}/lcaApache2/www/logs

  #opDo chown -R ${bystarUid} ${opAcct_homeDir}/lcaApache2
  opDo chown -R lsipusr:employee ${opAcct_homeDir}/lcaApache2
  opDo sudo -u root chmod -R  g+w ${opAcct_homeDir}/lcaApache2
}




function vis_virHostSiteConfigStdout {
    EH_assert [[ $# -eq 0 ]]
    EH_assert [[ "${bystarUid}_" != "MANDATORY_" ]]

  #G_abortIfNotRunningAsRoot

  opDoRet bystarAcctAnalyze ${bystarUid}

  opAcctInfoGet ${bystarUid}
  
  opDoExit opNetCfg_paramsGet ${opRunClusterName} ${opRunHostName}
    # ${opNetCfg_ipAddr} ${opNetCfg_netmask} ${opNetCfg_networkAddr} ${opNetCfg_defaultRoute}
    
#  thisIPAddress=`lpL3Hosts.sh -p clusterName=${opRunClusterName} -p hostName=${opRunHostName} -i givenHostGetIPaddr`

  opDo lpParamsBasicGet
  
  thisIPAddress=${lpDnsEntryIpAddr}

  dateTag=`date +%y%m%d%H%M%S`

    virHostSiteConfigStdoutSpecific_BCA_DEFAULT () {
  cat  << _EOF_
# VirDom xxx

_EOF_

    }

#   cat  << _EOF_
# # VirDom xxx
# ${thisIPAddress}
# www.${cp_acctMainBaseDomain}
# web.${cp_acctMainBaseDomain}
# ${cp_acctFactoryBaseDomain}
# ${cp_FirstName}.${cp_LastName}.${cp_nameSelector}.${cp_factoryBaseDomain} 
# web.${cp_acctFactoryBaseDomain}
# www.${cp_acctBynumberBaseDomain}
# web.${cp_acctBynumberBaseDomain}
# _EOF_

#echo "---------------------------------"

    function virHostSiteConfigStdoutSpecific_DEFAULT_DEFAULT {

  cat  << _EOF_
# VirtualHost for web.${cp_acctMainBaseDomain} Generated by ${G_myName} on ${dateTag}

<VirtualHost *:80>
    ServerName web.${cp_acctMainBaseDomain}
    ServerAdmin webmaster@${cp_acctMainBaseDomain}

    <Directory />
       Require all granted
    </Directory>

    DocumentRoot ${opAcct_homeDir}/lcaApache2/web/htdocs
    #ScriptAlias /cgi-bin/ "${opAcct_homeDir}/lcaApache2/web/cgi-bin/"	
    ErrorLog ${opAcct_homeDir}/lcaApache2/web/logs/error_log
    CustomLog ${opAcct_homeDir}/lcaApache2/web/logs/access_log common

    <Directory ${opAcct_homeDir}/lcaApache2/web/htdocs>
	Options +Indexes +FollowSymLinks +MultiViews
	AllowOverride all
	Order allow,deny
	allow from all
    </Directory>

    Alias /gallery ${opAcct_homeDir}/lcaApache2/web/htdocs/gallery

    <Directory ${opAcct_homeDir}/lcaApache2/web/htdocs/gallery>
      Options FollowSymLinks
      AllowOverride Limit Options FileInfo
    </Directory>
</VirtualHost>
_EOF_

    }
   
    bystarServiceSupportHookRun virHostSiteConfigStdoutSpecific

}


function vis_virHostSiteConfigUpdate {
    EH_assert [[ $# -eq 0 ]]
    EH_assert [[ "${bystarUid}_" != "MANDATORY_" ]]

  G_abortIfNotRunningAsRoot

  opDoRet bystarAcctAnalyze ${bystarUid}
  
  thisConfigFile="/etc/apache2/sites-available/web.${cp_acctMainBaseDomain}.conf"

    FN_fileSafeKeep ${thisConfigFile}

    vis_virHostSiteConfigStdout > ${thisConfigFile}

    opDo ls -l ${thisConfigFile}

    #FN_fileSymlinkUpdate ${thisConfigFile} "/etc/apache2/sites-enabled/web.${cp_acctMainBaseDomain}"
    opDo a2ensite web.${cp_acctMainBaseDomain}.conf

    opDo /etc/init.d/apache2 force-reload
}

function vis_virHostSiteConfigVerify {
    EH_assert [[ $# -eq 0 ]]
    EH_assert [[ "${bystarUid}_" != "MANDATORY_" ]]

  #G_abortIfNotRunningAsRoot

  opDoRet bystarAcctAnalyze ${bystarUid}
  
  thisConfigFile="/etc/apache2/sites-available/web.${cp_acctMainBaseDomain}"

  typeset tmpFile=$( FN_tempFile )

  vis_virHostSiteConfigStdout > ${tmpFile} 

  FN_fileCmpAndDiff ${thisConfigFile} ${tmpFile}
 
  FN_fileRmIfThere ${tmpFile} 
}

function vis_virHostSiteConfigShow {
    EH_assert [[ $# -eq 0 ]]
    EH_assert [[ "${bystarUid}_" != "MANDATORY_" ]]

  #G_abortIfNotRunningAsRoot

  opDoRet bystarAcctAnalyze ${bystarUid}
  
  thisConfigFile="/etc/apache2/sites-available/web.${cp_acctMainBaseDomain}"

  opDo ls -l ${thisConfigFile} 
}

function vis_a2ensite {
    G_funcEntry
    function describeF {  G_funcEntryShow; cat  << _EOF_
_EOF_
    }
    EH_assert [[ $# -eq 1 ]]

    typeset inSite="$1"

    opDo a2ensite "${inSite}"

    lpReturn
}

function vis_a2dissite {
    G_funcEntry
    function describeF {  G_funcEntryShow; cat  << _EOF_
_EOF_
    }
    EH_assert [[ $# -eq 1 ]]

    typeset inSite="$1"

    opDo a2dissite "${inSite}"

    lpReturn
}



function vis_virHostSiteConfigDelete {
    G_funcEntry
    function describeF {  G_funcEntryShow; cat  << _EOF_
_EOF_
    }
    EH_assert [[ $# -eq 0 ]]
    EH_assert [[ "${bystarUid}_" != "MANDATORY_" ]]

    G_abortIfNotRunningAsRoot

    opDoRet bystarAcctAnalyze ${bystarUid}
  
    opDo /bin/rm "/etc/apache2/sites-available/web.${cp_acctMainBaseDomain}" "/etc/apache2/sites-enabled/web.${cp_acctMainBaseDomain}"

    opDo /etc/init.d/apache2 force-reload
}


function vis_serviceDelete {
    G_funcEntry
    function describeF {  G_funcEntryShow; cat  << _EOF_
_EOF_
    }
    EH_assert [[ $# -eq 0 ]]
    EH_assert [[ "${bystarUid}_" != "MANDATORY_" ]]

    opDo vis_virHostSiteConfigDelete

    lpReturn
}


function vis_dnsUpdate {
  EH_assert [[ $# -eq 0 ]]
  EH_assert [[ "${bystarUid}_" != "MANDATORY_" ]]

  G_abortIfNotRunningAsRoot

  opDoRet mmaDnsServerHosts.sh -i hostIsOrigContentServer

  opDoRet bystarAcctAnalyze ${bystarUid}

  opDoExit opNetCfg_paramsGet ${opRunClusterName} ${opRunHostName}
    # ${opNetCfg_ipAddr} ${opNetCfg_netmask} ${opNetCfg_networkAddr} ${opNetCfg_defaultRoute}
    
  thisIPAddress=`lpL3Hosts.sh -p clusterName=${opRunClusterName} -p hostName=${opRunHostName} -i givenHostGetIPaddr`

    acctDnsUpdateSpecific_BCA_DEFAULT () {
	ANT_raw "Controlled Acct"
	# Get the Master Account -- Add to it relative

	opDo masterAcctBagpLoad

	if [ "${cp_master_acctFactoryBaseDomain}_" != "${cp_master_acctMainBaseDomain}_" ] ; then
	    bcaMainBaseDomain=${cp_DomainRel}.${cp_master_acctMainBaseDomain}

	    opDoRet mmaDnsEntryAliasUpdate www.${bcaMainBaseDomain} ${opRunHostName}
	    opDoRet mmaDnsEntryAliasUpdate web.${bcaMainBaseDomain} ${opRunHostName}
	fi

        bcaFactoryBaseDomain=${cp_DomainRel}.${cp_master_acctFactoryBaseDomain}

	    opDoRet mmaDnsEntryAliasUpdate www.${bcaFactoryBaseDomain} ${opRunHostName}
	    opDoRet mmaDnsEntryAliasUpdate web.${bcaFactoryBaseDomain} ${opRunHostName}

	opDo ls -l /etc/tinydns/origContent/data.origZones  1>&2
    }

    acctDnsUpdateSpecific_BYNAME_DEFAULT () {
	ANT_raw "Main (Master) Acct"

	if [ "${cp_acctFactoryBaseDomain}_" != "${cp_acctMainBaseDomain}_" ] ; then
	    opDoRet mmaDnsEntryAliasUpdate www.${cp_acctMainBaseDomain} ${opRunHostName}
	    opDoRet mmaDnsEntryAliasUpdate web.${cp_acctMainBaseDomain} ${opRunHostName}
	fi

	opDoRet mmaDnsEntryAliasUpdate ${cp_acctFactoryBaseDomain} ${opRunHostName}

	#
	# Backward compatibility
	#
	opDoRet mmaDnsEntryAliasUpdate ${cp_FirstName}.${cp_LastName}.${cp_nameSelector}.${cp_factoryBaseDomain}  ${opRunHostName}
	
	opDoRet mmaDnsEntryAliasUpdate web.${cp_acctFactoryBaseDomain} ${opRunHostName}

	opDoRet mmaDnsEntryAliasUpdate www.${cp_acctBynumberBaseDomain} ${opRunHostName}
	opDoRet mmaDnsEntryAliasUpdate web.${cp_acctBynumberBaseDomain} ${opRunHostName}

	opDo ls -l /etc/tinydns/origContent/data.origZones  1>&2
    }


    acctDnsUpdateSpecific_DEFAULT_DEFAULT () {
	ANT_raw "Main (Master) Acct"

	if [ "${cp_acctFactoryBaseDomain}_" != "${cp_acctMainBaseDomain}_" ] ; then
	    opDoRet mmaDnsEntryAliasUpdate www.${cp_acctMainBaseDomain} ${opRunHostName}
	    opDoRet mmaDnsEntryAliasUpdate web.${cp_acctMainBaseDomain} ${opRunHostName}
	fi

	opDoRet mmaDnsEntryAliasUpdate www.${cp_acctFactoryBaseDomain} ${opRunHostName}
	opDoRet mmaDnsEntryAliasUpdate web.${cp_acctFactoryBaseDomain} ${opRunHostName}

	opDoRet mmaDnsEntryAliasUpdate www.${cp_acctBynumberBaseDomain} ${opRunHostName}
	opDoRet mmaDnsEntryAliasUpdate web.${cp_acctBynumberBaseDomain} ${opRunHostName}

	opDo ls -l /etc/tinydns/origContent/data.origZones  1>&2
    }
   
    bystarServiceSupportHookRun acctDnsUpdateSpecific
}



function vis_dnsDelete {
  EH_assert [[ $# -eq 0 ]]
  EH_assert [[ "${bystarUid}_" != "MANDATORY_" ]]

  G_abortIfNotRunningAsRoot

  opDoExit mmaDnsServerHosts.sh -i hostIsOrigContentServer

  integer gotVal=0
  opDoRet bystarAcctAnalyze ${bystarUid} || gotVal=$?

  if [[ ${gotVal} -eq 0 ]] ; then

    opDoExit opNetCfg_paramsGet ${opRunClusterName} ${opRunHostName}

    opDoRet mmaDnsEntryMxUpdate ${byname_acct_baseDomain} ${opRunHostName}
    opDoRet mmaDnsEntryMxUpdate ${byname_acct_numberDomain} ${opRunHostName}
  else
    EH_problem "$0: not enough info."
    return 1
  fi
}
