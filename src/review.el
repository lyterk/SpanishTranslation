;;; review.el --- Review lines in a CSV or TSV file -*- lexical-binding: t -*-

;;; Header:

;; Maintainer: Kevin Lyter <code@lyterk.com>
;; Author: Kevin Lyter <code@lyterk.com>
;; Version 0.1.0
;; Package-Requires ((emacs "25.3"))
;; 
;;; Commentary:
;; Review, line-by-line, a CSV file and mark it with directives
;; 
;;; Code:
(require 'cl-lib)
(require 'json)

(defcustom my/card-review/state-file "/tmp/card-review-state-file.json"
  "Location to persist the state of the card-review"
  :type 'file
  :group 'personal-settings)

(defun my/card-review/fullscreen-arrow-prompt (prompt callback)
  "Display PROMPT in a fullscreen buffer and accept arrow key input.
When the user presses an arrow key, call CALLBACK with the symbol
`left, `right, `up, or `down, and kill the buffer."
  (let ((buf (get-buffer-create "*Kevin Prompt*")))
    (switch-to-buffer buf)
    (with-current-buffer buf
      (erase-buffer)
      (insert prompt)
      (text-scale-adjust 5)
      (goto-char (point-min))
      (let* ((my-input (read-event))
             (directions '(left right up down))
             (parsed-direction
              (if (memq my-input directions)
                  my-input
                'quit)))
        (progn
          (funcall callback parsed-direction)
          (kill-buffer)
          parsed-direction)))))

(my/card-review/fullscreen-arrow-prompt
 "Choose a direction."
 'my/card-review/callback-action)


(defun my/card-review/spanish-directions (direction)
  (cond
   ((eq direction 'left) 'undo)
   ((eq direction 'right) 'advance)
   ((eq direction 'up) 'updated)
   ((eq direction 'down) 'more-review)
   (t 'quit)))

(defun my/card-review/callback-action (directive)
  (cond
   ((eq directive 'undo) )))


(defun my/card-review/new-directive (directive)
  (let ((row (aref my/card-review/rich-lines my/card-review/index)))
    ;; Move current directive to old
    (puthash "prev-directive" (gethash "directive" row) row)
    ;; Remove the current directive
    (remhash "directive" row)
    ;; Put the new directive in
    (puthash "directive" directive row)))

(defun my/card-review/read-csv-file (filename)
  (with-temp-buffer
    (insert-file-contents filename)
    (let* ((file-lines (split-string (buffer-string) "\n" t))
           (begin-index 0)
           (rich-lines (cl-map
                        'vector ;; `json-serialize only handles vectors'
                        (lambda (line)
                          (let ((ht (make-hash-table)))
                            (puthash "line" line ht)
                            (puthash "directive" "unreviewed" ht)
                            ht))
                        file-lines))
           (my-state (make-hash-table)))
      (puthash "lines" rich-lines my-state)
      (puthash "index" index my-state)
      (setq my/card-review/index begin-index
            my/card-review/rich-lines rich-lines
            my/card-review/state my-state))))

(defun my/card-review/persist-state ()
  "Write the state list to a json file"
  (let ((ht (make-hash-table)))
    (puthash "lines" my/card-review/rich-lines ht)
    (puthash "index" my/card-review/index ht)
    (with-temp-file my/card-review/state-file
      (insert (json-serialize ht)))))


(defun my/card-review/load-state ()
  "Pick up the file and resume"
  (let* ((state (with-temp-buffer
                  (insert-file-contents my/card-review/state-file)
                  (json-parse-buffer)))
         (rich-lines (gethash "lines" state))
         (index (gethash "index" state)))
    (setq my/card-review/index index
          my/card-review/rich-lines rich-lines
          my/card-review/state state)))

;; (defun my/card-review/process-line (line)
;;   (let* ((length-fields (length (split-string line "\t" t t))))
;;     ))

(setq test-line "la locura	insanity, madness, dementia	0.12")
my/card-review/rich-lines
(puthash "hello" "something-new" (aref my/card-review/rich-lines 0))
;;; review.el ends here
