=============
keystoneauth1
=============

.. _keystoneauth1_3.6.1:

3.6.1
=====

.. _keystoneauth1_3.6.1_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/fix-get-all-version-data-a01ee58524755b9b.yaml @ 0bebdaf0f90deef5121234ac98daa58e6f1f0f77

- The docstring for ``keystoneauth1.session.Session.get_all_version_data``
  correctly listed ``'public'`` as the default value, but the argument list
  had ``None``. The default has been fixed to match the documented value.


.. _keystoneauth1_3.6.0:

3.6.0
=====

.. _keystoneauth1_3.6.0_New Features:

New Features
------------

.. releasenotes/notes/expose-endpoint-status-6195a6b76d8a8de8.yaml @ 43c6e378f944227068ed815d84c124d6a7cc9d08

- Added a 'status' field to the `EndpointData` object which contains a
  canonicalized version of the information in the status field of discovery
  documents.

.. releasenotes/notes/serice-type-aliases-249454829c57f39a.yaml @ 79cd91e75580511171a3a61dc6f3c70e275f6348

- Added support for service-type aliases as defined in the Service Types
  Authority when doing catalog lookups.

