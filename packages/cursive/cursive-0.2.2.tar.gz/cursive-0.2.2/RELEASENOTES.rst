=======
cursive
=======

.. _cursive_0.2.0:

0.2.0
=====

.. _cursive_0.2.0_Prelude:

Prelude
-------

.. releasenotes/notes/add-certificate-validation-68a1ffbd5369a8d1.yaml @ ad879a1fbccfa31fdedd69e3193e9bf12a15f943

The cursive library supports the verification of digital signatures. However, there is no way currently to validate the certificate used to generate a given signature. Adding certificate validation improves the security of signature verification when each is used together.


.. _cursive_0.2.0_New Features:

New Features
------------

.. releasenotes/notes/add-certificate-validation-68a1ffbd5369a8d1.yaml @ ad879a1fbccfa31fdedd69e3193e9bf12a15f943

- Adds a variety of certificate utility functions that inspect certificate attributes and extensions for different settings.

.. releasenotes/notes/add-certificate-validation-68a1ffbd5369a8d1.yaml @ ad879a1fbccfa31fdedd69e3193e9bf12a15f943

- Adds the CertificateVerificationContext class which uses a set of trusted certificates to conduct certificate validation, verifying that a given certificate is part of a certificate chain rooted with a trusted certificate.

.. releasenotes/notes/add-certificate-validation-68a1ffbd5369a8d1.yaml @ ad879a1fbccfa31fdedd69e3193e9bf12a15f943

- Adds a verify_certificate method that loads all certificates needed for certificate validation from the key manager and uses them to create a CertificateVerificationContext object. The context is then used to determine if a certificate is valid.


.. _cursive_0.2.0_Upgrade Notes:

Upgrade Notes
-------------

.. releasenotes/notes/add-certificate-validation-68a1ffbd5369a8d1.yaml @ ad879a1fbccfa31fdedd69e3193e9bf12a15f943

- The addition of certificate validation as a separate operation from the signature verification process preserves backwards compatibility. Signatures previously verifiable with cursive will still be verifiable. However, their signing certificates may not be valid. Each signing certificate should be checked for validity before it is used to conduct signature verification.


.. _cursive_0.2.0_Security Issues:

Security Issues
---------------

.. releasenotes/notes/add-certificate-validation-68a1ffbd5369a8d1.yaml @ ad879a1fbccfa31fdedd69e3193e9bf12a15f943

- The usage of certificate validation with the signature verification process improves the security of signature verification. A signature should not be considered valid unless its corresponding certificate is also valid.


.. _cursive_0.2.0_Other Notes:

Other Notes
-----------

.. releasenotes/notes/add-certificate-validation-68a1ffbd5369a8d1.yaml @ ad879a1fbccfa31fdedd69e3193e9bf12a15f943

- The CertificateVerificationContext is built using a set of trusted certificates. However, to conduct certificate verification the context builds the full certificate chain, starting with the certificate to validate and ending with the self-signed root certificate. If this self-signed root certificate is not present in the context, or if one of the intermediate certificates is not present in the context, the certificate chain cannot be built and certificate validation will fail.

