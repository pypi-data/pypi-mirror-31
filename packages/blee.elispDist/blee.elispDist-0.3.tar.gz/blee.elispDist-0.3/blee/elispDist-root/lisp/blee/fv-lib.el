;;; -*- Mode: Emacs-Lisp; -*-
;; (setq debug-on-error t)
;; Start Example: (replace-string "moduleName" "fv-lib")  (replace-string "moduleTag:" "fv:")

(lambda () "
*  [[elisp:(org-cycle)][| ]]  *Short Desription*  :: Library (fv:), for handelling File_Var [[elisp:(org-cycle)][| ]]
* 
")


;;;#+BEGIN: bx:dblock:global:org-controls :disabledP "false" :mode "auto"
(lambda () "
*  /Controls/ ::  [[elisp:(org-cycle)][| ]]  [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
*  /Maintain/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]] 
*      ================
")
;;;#+END:

;;;#+BEGIN: bx:dblock:global:org-contents-list :disabledP "false" :mode "auto"
(lambda () "
*      ################ CONTENTS-LIST ###############
*  [[elisp:(org-cycle)][| ]]  *Document Status, TODOs and Notes*          ::  [[elisp:(org-cycle)][| ]]
")
;;;#+END:

(lambda () "
**  [[elisp:(org-cycle)][| ]]  Idea      ::  Description   [[elisp:(org-cycle)][| ]]
")


(lambda () "
* TODO [[elisp:(org-cycle)][| ]]  Description   :: *Info and Xrefs* UNDEVELOPED just a starting point <<Xref-Here->> [[elisp:(org-cycle)][| ]]
")


;;;#+BEGIN: bx:dblock:lisp:loading-message :disabledP "false" :message "fv-lib"
(lambda () "
*  [[elisp:(org-cycle)][| ]]  "Loading..."                :: Loading Announcement Message fv-lib [[elisp:(org-cycle)][| ]]
")

(blee:msg "Loading: fv-lib")
;;;#+END:


(lambda () "
*  [[elisp:(org-cycle)][| ]]  Requires                    :: Requires [[elisp:(org-cycle)][| ]]
")


(lambda () "
*  [[elisp:(org-cycle)][| ]]  Top Entry                   :: fv:main-init [[elisp:(org-cycle)][| ]]
")


(lambda () "
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || defun        :: (fv:main-init) [[elisp:(org-cycle)][| ]]
")

(defun fv:main-init ()
  "Desc:"
  nil
  )

;; (setq tmpVar11 "")
;; (message (get 'tmpVar11 'description))
;; (symbol-plist 'tmpVar11)

;; (fv:read-var-string "/libre/ByStar/InitialTemplates/activeDocs/blee/syncUpdate/virBox/iims/lcaVirshManage.sh/params/kvmHost/fvtn/curValue")
(lambda () "
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || defun        :: (fv:read-var-string file) [[elisp:(org-cycle)][| ]]
  ")


(defun fv:read-as-string (file)
  "Given File, read its content as string and return that string."
  (replace-regexp-in-string "\n$" "" (bx:file-string file))
  )


;; (bx:file-string "/libre/ByStar/InitialTemplates/activeDocs/blee/syncUpdate/virBox/iims/lcaVirshManage.sh/params/kvmHost/fvtn/curValue") tmpVar11)
;; (fv:leaf:read-var-string "/libre/ByStar/InitialTemplates/activeDocs/blee/syncUpdate/virBox/iims/lcaVirshManage.sh/params/kvmHost/fvtn/curValue" 'tmpVar11)
(lambda () "
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || defun        :: (fv:leaf:read-var-string file propVar) [[elisp:(org-cycle)][| ]]
  ")

(defun fv:leaf:read-var-as-string (file propVar)
  "Given File, write its content as string as a property of propVar."
  (let (
	(varName (file-name-nondirectory file))
	)
    (blee:eval-string
     (format "(put '%s '%s \"%s\")"
	     propVar
	     varName
	     (replace-regexp-in-string "\n$" "" (bx:file-string file))
	     ))
    varName))
;; (setq tmpVar11 "")
;; (symbol-plist 'tmpVar11)
;; (fv:node:read-var-string "/libre/ByStar/InitialTemplates/activeDocs/blee/syncUpdate/virBox/iims/lcaVirshManage.sh/params/kvmHost/fvtn" 'tmpVar11)
(lambda () "
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || defun        :: (fv:node:read-var-string dir propVar) [[elisp:(org-cycle)][| ]]
  ")

(defun fv:node:read-var-as-string (dir propVar)
  "Given File, write its content as string as a property of propVar."
  (mapc
   (lambda (x)
     (fv:leaf:read-var-as-string x propVar)     
     )
   (blee:fn:dir:*-relevant dir)   
   ))

;;;#+BEGIN: bx:dblock:lisp:provide :disabledP "false" :lib-name "fv-lib"
(lambda () "
*  [[elisp:(org-cycle)][| ]]  Provide                     :: Provide [[elisp:(org-cycle)][| ]]
")

(provide 'fv-lib)
;;;#+END:


(lambda () "
*  [[elisp:(org-cycle)][| ]]  Common        :: /[dblock] -- End-Of-File Controls/ [[elisp:(org-cycle)][| ]]
#+STARTUP: showall
")

;;; local variables:
;;; no-byte-compile: t
;;; end:
