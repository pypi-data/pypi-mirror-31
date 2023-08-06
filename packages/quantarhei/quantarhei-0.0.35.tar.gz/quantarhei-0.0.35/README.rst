|Build Status| |DocBuild Status| |Coverage|

QUANTArhei: Open Quantum System Theory for Molecular Systems 
============================================================

Quantarhei is a Molecular Open Quantum Systems Simulator written predominantly
in Python. Its name is derived from the famous aphorism "Panta rhei" of the
Greek philosopher Heraclitus of Ephesus. "Panta rhei" means "Everything flows"
or "Everything is in flux" which is quite fitting when you change Panta into
Quanta.

In "Quantarhei" the last four letter ("rhei") should be written in Greek,
i.e. (using LateX convention) "\\rho \\epsilon \\iota". 

----

Quantarhei is in flux, but it already provides helper classes to define
molecules, their aggregates and their interaction with external environment.
It can calculate absorption spectra of individual molecules and their
aggregates and excitation energy transfer dynamics using various types
of Redfield and Foerster theories.

Quantarhei provides Python code (optimized with Numpy) for all its implemented
methods and theories, and allows extensions and replacements of the reference
Python code with optimised routines written in C, Fortran or other lower level
languages.

In the first development stage, we concentrate on bringing to you tools
to quickly build essential components of a quantum mechanical simulation,
such as Hamiltonian, relaxation tensors, various initial
conditions for density matrix etc.

Quantarhei is at its experimental stage. 
Current version is 0.0.33

Quantarhei is available in source form on GitHub and from PyPI for installation
with the pip command.


Acknowledgements
================

The work on Quantarhei is supported by

|NFN|_

.. |NFN| replace:: **Neuron Fund for Support of Science**
.. _NFN: http://www.nfneuron.cz

through the Impuls grant in physics 2014 (2015-2017)

and

|GACR|_

.. |GACR| replace:: **Czech Science Foundation (GACR)**
.. _GACR: http://www.gacr.cz
                                               

through grants: 14-25752S (2014-2016) and 17-22160S (2017- )


New in 0.0.35
=============

For users:
 - Method get_DensityMatrix() of the Aggregate class improved. It accepts some new options which makes specification of desired density matrix more flexible
 - Experimental implementation of circular and linear dichroisms and fluorescence spectra
 - Documentation is now available on readthedocs.org. A badge |DocBuild Status| which informations about the status of automatic documentation builds was added to README
 - Many small improvements and bug fixes 

For developers:
 - The code is now hosted on travis-ci.com and the builds are tested after every commit. Corresponding badge |Build Status|_ has been added to README
 - The code is now hosted on codecov.com and its coverage by tests is measured. Corresponding badge showing the coverage |Coverage|_ has beed added to README


New in 0.0.34
=============

For users
 - Some issues with addition of bath correlation functions was fixed
 - First entry in a database of literature bath correlation functions was created: the vibrational part of the FMO spectral density from Wendling et al., (2004)
 - Aggregate can return a matrix of Franck-Condon factors (get_FC_factor_matrix())
 - Aggregate can transform excited state site-basis shifted vibrational representation of an arbitrary operator to the unshifted (ground state) one (transform_2_unshifted(A, inverse=True/False) )
 - Several new tested examples
 - RelaxationTensors (Redfield, Foerster, Lindblad, etc.) can now be multiplied by a constant or added (addition only if they are in tensor, i. e. not in operator, form)
 - Tested examples can be fetched into IPython notebook or Python/IPython console by %example magic command or fetch_example function from quantarhei.wizard.magic module
 - Small improvements and bug fixes

New in 0.0.33
=============

For users:

- Evolution superoperators for relaxation tensors with constant coefficients (EvolutionSuperOperator class)
- Liouville pathway analysis including relaxation pathways (in Aggregate class)
- Small improvements and bug fixes

For developers:

- Aggregate class is broken into smaller pieces which snowball the functionality. Basic class is AggregateBase; new functions of this powerful class are defined in separate child classes. Aggregate class inherits from the whole chain of classes 
- quantarhei.REAL and quantarhei.COMPLEX types should be now used for numpy arrays throughout the package. These types can be controlled and with it the used numerical precision and memory needs



New in 0.0.32
=============

For users:

- Electronic Lindblad form for vibronic Frenkel exciton model
- Propagation with relaxation tensor (in particular Redfield and Time-dependent Redfield) in operator representation (where applicable it is much faster than with the tensorial representation)
- Redfield tensor and Time-dependent Redfield tensor can be calculated for a model with arbitrary number of vibrational states
- Aggregate can vibrationally trace arbitrary operator defined on its Hilbert space
- Small improvements and bug fixes



New in version 0.0.31
=====================

For users:

- Arbitrary time independent Lindblad form 
- quantarhei.wizard module which contains IPython magic commands and some helpful Python console commands
- Simulation templates which can be fetched into IPython notebooks or console by %template  magic command (IPython) or fetch_template (console and IPython)
- Part of the test suit available for installed Quantarhei package
- Some small improvements and bug fixes

For developers:

- Makefile is back in the package root directory
- examples directory depleted in favor of quantarhei/wizard/examples directory
- New tests under quantarhei/tests directory (mostly unit tests which contain plots)
- pytest required to run newtests with matplotlib plots
 

.. |DocBuild Status| image:: https://readthedocs.org/projects/quantarhei/badge/?version=latest
   :target: http://quantarhei.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
   
.. |Build Status| image:: https://travis-ci.com/tmancal74/quantarhei.svg?branch=master
   :target: https://travis-ci.com/tmancal74/quantarhei
   :alt: Build Status
 
.. |Coverage| image:: https://img.shields.io/codecov/c/github/tmancal74/quantarhei.svg
   :target: https://codecov.io/gh/tmancal74/quantarhei