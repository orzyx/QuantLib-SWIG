
; Copyright (C) 2000, 2001, 2002 RiskMap srl
;
; This file is part of QuantLib, a free-software/open-source library
; for financial quantitative analysts and developers - http://quantlib.org/
;
; QuantLib is free software: you can redistribute it and/or modify it under the
; terms of the QuantLib license.  You should have received a copy of the
; license along with this program; if not, please email ferdinando@ametrano.net
; The license is also available online at http://quantlib.org/html/license.html
;
; This program is distributed in the hope that it will be useful, but WITHOUT
; ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
; FOR A PARTICULAR PURPOSE.  See the license for more details.

; $Id$


; usage
(define (usage)
  (format #t "Usage: mzscheme -r setup scm command\n")
  (format #t "  Commands:\n")
  (format #t "    wrap             generate wrappers from SWIG interfaces\n")
  (format #t "    build            build QuantLib-MzScheme\n")
  (format #t "    install          install QuantLib-MzScheme\n")
  ;(format #t "    sdist            create source distribution\n")
  ;(format #t "    bdist            create binary distribution\n")
  (exit))


; current QuantLib version
(define version "0.3.1a0-cvs")

; files
(define info-files
  (list "Authors.txt" "ChangeLog.txt" "Contributors.txt"
        "LICENSE.TXT" "History.txt" "README.txt"))
(define source-files
  (list "QuantLib.scm" "quantlib_wrap.cpp"))
(define binary-files
  (list "QuantLibc.so"))
(define scripts
  (list "setup.scm"))
(define SWIG-interfaces
  (list "quantlib.i"
        "ql.i"
        "common.i"
        "blackmodel.i"
        "calendars.i"
        "capfloor.i"
        "currencies.i"
        "date.i"
        "daycounters.i"
        "distributions.i"
        "functions.i"
        "history.i"
        "indexes.i"
        "instruments.i"
        "interpolation.i"
        "linearalgebra.i"
        "marketelements.i"
        "montecarlo.i"
        "null.i"
        "observer.i"
        "operators.i"
        "optimizers.i"
        "options.i"
        "piecewiseflatforward.i"
        "randomnumbers.i"
        "riskstatistics.i"
        "segmentintegral.i"
        "statistics.i"
        "swap.i"
        "swaption.i"
        "termstructures.i"
        "types.i"
        "vectors.i"
        ; to be removed
        "old_pricers.i"
        "old_volatility.i"))
(define test-files
  (list "capfloor.scm"
        "common.scm"
        "covariance.scm"
        "date.scm"
        "daycounters.scm"
        "distributions.scm"
        "europeanoption.scm"
        "instruments.scm"
        "marketelements.scm"
        "operators.scm"
        "piecewiseflatforward.scm"
        "riskstatistics.scm"
        "segmentintegral.scm"
        "simpleswap.scm"
        "solvers1d.scm"
        "statistics.scm"
        "swaption.scm"
        "termstructures.scm"
        ; to be removed
        "old_pricers.scm"))
(define test-support-files
  (list "unittest.scm"
        "utilities.scm"
        "quantlib-test-suite.scm"))

; commands

(define (wrap)
  (display "Generating Guile bindings for QuantLib...") (newline)
  (let ((swig-dir "./SWIG"))
    (if (not (file-exists? swig-dir))
        (set! swig-dir "../../SWIG"))
    (system (string-append "swig -guile -c++ -Linkage simple "
                           "-scmstub QuantLib.scm "
                           (format #f "-I~A " swig-dir)
                           "-o quantlib_wrap.cpp "
                           "quantlib.i"))))

(define (build)
  (define (string-split s)
    (let ((n (string-length s))
          (spcs '()))
      (do ((i 0 (+ i 1)))
          ((= i n))
        (if (char=? (string-ref s i) #\space)
            (set! spcs (cons i spcs))))
      (let ((begins (cons 0 (map (lambda (i) (+ i 1)) 
                                 (reverse spcs))))
            (ends (reverse (cons n spcs))))
        (map (lambda (b e) (substring s b e)) begins ends))))
  (display "Building QuantLib-Guile...") (newline)
  (let ((c++-compiler (getenv "CC"))
        (c-flags (getenv "CFLAGS"))
        (c++-flags (getenv "CXXFLAGS")))
    (if (not c++-compiler) (set! c++-compiler "g++"))
    (let ((flags '("-DHAVE_CONFIG_H" "-c" "-fpic"
                   "-I/usr/include" "-I/usr/local/include")))
      (if c-flags
          (set! flags (append flags (string-split c-flags))))
      (if c++-flags
          (set! flags (append flags (string-split c++-flags))))
      (let ((command (apply string-append 
                            (map
                             (lambda (s) (string-append s " "))
                             (append (list c++-compiler)
                                     flags
                                     (list "quantlib_wrap.cpp"))))))
        (display command) (newline)
        (system command)))
    (let ((command (string-append c++-compiler " -shared "
                         "quantlib_wrap.o "
                         "-L/usr/local/lib "
                         "-lQuantLib "
                         "-o QuantLibc.so")))
      (display command) (newline)
      (system command))))

(define (test)
  (format #t "Testing QuantLib-Guile ~A\n" version)
  (let ((this-dir (getcwd)))
    (set! %load-path (cons this-dir %load-path))
    (chdir "./test")
    (load "quantlib-test-suite.scm")
    (chdir this-dir)
    (set! %load-path (cdr %load-path))))

(define (install)
  (define (find-install-path path)
    (if (null? path) 
        #f
        (let ((dir (car path))
              (cwd (getcwd)))
          (if (and (file-exists? dir) 
                   (file-is-directory? dir)
                   (not (string=? dir "."))
                   (not (string=? dir cwd)))
              dir
              (find-install-path (cdr path))))))
  (display "Installing QuantLib-Guile...") (newline)
  (let ((install-path (find-install-path %load-path)))
    (for-each (lambda (file)
                (system (format #f "install -m 0555 ~A ~A"
                                file
                                (string-append install-path
                                               "/"
                                               file))))
              '("QuantLib.scm" "QuantLibc.so"))))


; SDist = Command.new {
; 	Wrap.execute
; 	puts "Packing source distribution..."
; 	distDir = "QuantLib-Ruby-#{Version}"
; 	raise "Directory #{distDir} already exist" if File.exists? distDir
; 	swigDir = distDir+"/SWIG"
; 	testDir = distDir+"/test"
; 	[distDir,swigDir,testDir].each { |path| File.makedirs path }
; 	Info.each       { |file| File.syscopy file, distDir }
; 	Sources.each    { |file| File.syscopy file, distDir }
; 	Scripts.each    { |file| File.syscopy file, distDir }
; 	Interfaces.each { |file| File.syscopy '../SWIG/'+file, swigDir }
; 	Tests.each      { |file| File.syscopy 'test/'+file, testDir }
; 	cfg = Config::MAKEFILE_CONFIG
; 	case cfg['host_os']
; 	  when 'mswin32'
;     	system "zip -q -r #{distDir}.zip #{distDir}/"
; 	  when 'linux'
;     	system "tar cfz #{distDir}.tar.gz #{distDir}/"
;       else
;         puts "Unknown host: " + cfg['host_os']
;     end
; }

; BDist = Command.new {
; 	Wrap.execute
; 	Build.execute
; 	puts "Packing binary distribution..."
; 	distDir = "QuantLib-Ruby-#{Version}"
; 	raise "Directory #{distDir} already exist" if File.exists? distDir
; 	swigDir = distDir+"/SWIG"
; 	testDir = distDir+"/test"
; 	[distDir,swigDir,testDir].each { |path| File.makedirs path }
; 	Info.each       { |file| File.syscopy file, distDir }
; 	Sources.each    { |file| File.syscopy file, distDir }
; 	Binaries.each   { |file| File.syscopy file, distDir }
; 	Scripts.each    { |file| File.syscopy file, distDir }
; 	Interfaces.each { |file| File.syscopy '../SWIG/'+file, swigDir }
; 	Tests.each      { |file| File.syscopy 'test/'+file, testDir }
; 	system "tar cfz #{distDir}.#{Config::CONFIG['arch']}.tar.gz #{distDir}/"
; }



(define available-commands
  (list (cons "wrap"    wrap)
        (cons "build"   build)
        (cons "test"    test)
        (cons "install" install)))

; parse command line
(let ((argv (command-line)))
  (if (not (= (length argv) 2))
      (usage))
  (let ((command (assoc (cadr argv) available-commands)))
    (if command
        ((cdr command))
        (usage))))
