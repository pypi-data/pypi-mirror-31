=======
hacking
=======

.. _hacking_1.1.0:

1.1.0
=====

.. _hacking_1.1.0_Prelude:

Prelude
-------

.. releasenotes/notes/rocky-intermediate-release-60db6e8f66539e4b.yaml @ 61cfa10314cec4dc751ca02a0e9f3631ee6b94be

This release includes below changes:

- Transition to flake8 2.6.x:

  * flake8 2.6.x performed the conversion to pycodestyle (which is
    the new name of pep8). Remove the explicit dependencies of
    hacking as flake8 is going to pull in mccabe, pyflakes and
    pycodestyle in the versions that are needed.

- Allow 'wraps' to be an alternative to autospec:

  * Don't cause an H210 error if the mock.patch/mock.patch.object call uses
    the 'wraps' keyword. As that serves the same purpose in catching wrong
    attributes.


.. _hacking_1.0.0:

1.0.0
=====

.. _hacking_1.0.0_New Features:

New Features
------------

.. releasenotes/notes/start-of-queens-c3024ebbb49aef6f.yaml @ e51e8aa092e4a91f3b0b57eb0c691a0af4f23cab

- This release includes new checks, which are disabled by default:
  
  * [H210] Require 'autospec', 'spec', or 'spec_set' in mock.patch/mock.patch.object calls
  
  * [H204] Use assert(Not)Equal to check for equality.
  
  * [H205] Use assert(Greater|Less)(Equal) for comparison.

