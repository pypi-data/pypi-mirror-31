#!/bin/bash

IimBriefDescription="MODULE BinsPrep based on apt based seedSubjectBinsPrepDist.sh"

ORIGIN="
* Revision And Libre-Halaal CopyLeft -- Part of [[http://www.by-star.net][ByStar]] -- Best Used With [[http://www.by-star.net/PLPC/180004][Blee]] or [[http://www.gnu.org/software/emacs/][Emacs]]
"

####+BEGIN: bx:dblock:bash:top-of-file :vc "cvs" partof: "bystar" :copyleft "halaal+brief"
typeset RcsId="$Id: lcaApache2BinsPrep.sh,v 1.1.1.1 2016-06-08 23:49:51 lsipusr Exp $"
# *CopyLeft*
# Copyright (c) 2011 Neda Communications, Inc. -- http://www.neda.com
# See PLPC-120001 for restrictions.
# This is a Halaal Poly-Existential intended to remain perpetually Halaal.
####+END:

__author__="
* Authors: Mohsen BANAN, http://mohsen.banan.1.byname.net/contact
"


####+BEGIN: bx:dblock:lsip:bash:seed-spec :types "seedSubjectBinsPrepDist.sh"
SEED="
* /[dblock]/--Seed/: /opt/public/osmt/bin/seedSubjectBinsPrepDist.sh
"
if [ "${loadFiles}" == "" ] ; then
    /opt/public/osmt/bin/seedSubjectBinsPrepDist.sh -l $0 "$@" 
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
*      ################  CONTENTS-LIST ###############
*      ======[[elisp:(org-cycle)][Fold]]====== *[Current-Info:]* Module Description, Notes (Tasks/Todo Lists, etc.)
_CommentEnd_
function vis_moduleDescription {  cat  << _EOF_
**      ====[[elisp:(org-cycle)][Fold]]==== /Module Desrciption/
_EOF_
}

_CommentBegin_
*      ======[[elisp:(org-cycle)][Fold]]====== *[Related-Xrefs:]* <<Xref-Here->>  -- External Documents 
Xref-Here-
**      ====[[elisp:(org-cycle)][Fold]]==== [[file:/libre/ByStar/InitialTemplates/activeDocs/bxServices/versionControl/fullUsagePanel-en.org::Xref-VersionControl][Panel Roadmap Documentation]]
_CommentEnd_

_CommentBegin_
*      ======[[elisp:(org-cycle)][Fold]]====== Components List
_CommentEnd_

#apt-cache search something | egrep '^something'

function pkgsList_DEFAULT_DEFAULT {
    G_funcEntry
    function describeF {  G_funcEntryShow; cat  << _EOF_
_EOF_
    }

    #  [[elisp:(lsip-local-run-command "apt-cache search something | egrep '^something'")][apt-cache search something | egrep '^something']]

    itemOrderedList=( 
	"apache2"
	apache2_utils
	#"apache2_common" 
	"libapache2_mod_python" 
	"libapache2_mod_php5"
	"libapache2_mod_wsgi"
	"libapache2_mod_proxy_html"
	"apache2_suexec_pristine"
    )

    itemOptionalOrderedList=()
    itemLaterOrderedList=()
}

distFamilyGenerationHookRun pkgsList


_CommentBegin_
*      ======[[elisp:(org-cycle)][Fold]]====== Module Specific Additions -- examplesHook
_CommentEnd_


function examplesHookPost {
  cat  << _EOF_
----- ADDITIONS -------
${G_myName} -i moduleDescription
_EOF_
}

####+BEGIN: bx:dblock:lsip:binsprep:apt :module "apache2"
_CommentBegin_
*      ======[[elisp:(org-cycle)][Fold]]====== Apt-Pkg: apache2
_CommentEnd_
item_apache2 () { distFamilyGenerationHookRun binsPrep_apache2; }

binsPrep_apache2_DEFAULT_DEFAULT () { binsPrepAptPkgNameSet "apache2"; }

####+END:

####+BEGIN: bx:dblock:lsip:binsprep:apt :module "apache2-utils"
_CommentBegin_
*      ======[[elisp:(org-cycle)][Fold]]====== Apt-Pkg: apache2-utils
_CommentEnd_
item_apache2_utils () { distFamilyGenerationHookRun binsPrep_apache2_utils; }

binsPrep_apache2_utils_DEFAULT_DEFAULT () { binsPrepAptPkgNameSet "apache2-utils"; }

####+END:


####+BEGIN: bx:dblock:lsip:binsprep:apt :module "apache2-common"
_CommentBegin_
*      ======[[elisp:(org-cycle)][Fold]]====== Apt-Pkg -- Obsoleted: apache2-common
_CommentEnd_
item_apache2_common () { distFamilyGenerationHookRun binsPrep_apache2_common; }

binsPrep_apache2_common_DEFAULT_DEFAULT () { binsPrepAptPkgNameSet "apache2-common"; }

####+END:

####+BEGIN: bx:dblock:lsip:binsprep:apt :module "libapache2-mod-python"
_CommentBegin_
*      ======[[elisp:(org-cycle)][Fold]]====== Apt-Pkg: libapache2-mod-python
_CommentEnd_
item_libapache2_mod_python () { distFamilyGenerationHookRun binsPrep_libapache2_mod_python; }

binsPrep_libapache2_mod_python_DEFAULT_DEFAULT () { binsPrepAptPkgNameSet "libapache2-mod-python"; }

####+END:

####+BEGIN: bx:dblock:lsip:binsprep:apt :module "libapache2-mod-php5"
_CommentBegin_
*      ======[[elisp:(org-cycle)][Fold]]====== Apt-Pkg: libapache2-mod-php5
_CommentEnd_
item_libapache2_mod_php5 () { distFamilyGenerationHookRun binsPrep_libapache2_mod_php5; }

binsPrep_libapache2_mod_php5_DEFAULT_DEFAULT () { binsPrepAptPkgNameSet "libapache2-mod-php5"; }

####+END:

####+BEGIN: bx:dblock:lsip:binsprep:apt :module "libapache2-mod-wsgi"
_CommentBegin_
*      ======[[elisp:(org-cycle)][Fold]]====== Apt-Pkg: libapache2-mod-wsgi
_CommentEnd_
item_libapache2_mod_wsgi () { distFamilyGenerationHookRun binsPrep_libapache2_mod_wsgi; }

binsPrep_libapache2_mod_wsgi_DEFAULT_DEFAULT () { binsPrepAptPkgNameSet "libapache2-mod-wsgi"; }

####+END:

####+BEGIN: bx:dblock:lsip:binsprep:apt :module "libapache2-mod-proxy-html"
_CommentBegin_
*      ======[[elisp:(org-cycle)][Fold]]====== Apt-Pkg: libapache2-mod-proxy-html
_CommentEnd_
item_libapache2_mod_proxy_html () { distFamilyGenerationHookRun binsPrep_libapache2_mod_proxy_html; }

binsPrep_libapache2_mod_proxy_html_DEFAULT_DEFAULT () { binsPrepAptPkgNameSet "libapache2-mod-proxy-html"; }

####+END:



####+BEGIN: bx:dblock:lsip:binsprep:apt :module "apache2-suexec-pristine"
_CommentBegin_
*      ======[[elisp:(org-cycle)][Fold]]====== Apt-Pkg: apache2-suexec-pristine
_CommentEnd_
item_apache2_suexec_pristine () { distFamilyGenerationHookRun binsPrep_apache2_suexec_pristine; }

binsPrep_apache2_suexec_pristine_DEFAULT_DEFAULT () { binsPrepAptPkgNameSet "apache2-suexec-pristine"; }

####+END:

_CommentBegin_
*      ================ /[dblock] -- End-Of-File Controls/
_CommentEnd_
#+STARTUP: showall
#local variables:
#major-mode: sh-mode
#fill-column: 90
# end:
####+END:

