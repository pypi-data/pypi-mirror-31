==================
keystonemiddleware
==================

.. _keystonemiddleware_5.1.0:

5.1.0
=====

.. _keystonemiddleware_5.1.0_New Features:

New Features
------------

.. releasenotes/notes/bug-1762362-3d092b15c7bab3a4.yaml @ a78a25ea23a940fcc510226a2dd33731d81fb213

- [`bug 1762362 <https://bugs.launchpad.net/keystonemiddleware/+bug/1762362>`_] The value of the header "WWW-Authenticate" in a 401 (Unauthorized) response now is double quoted to follow the RFC requirement.


.. _keystonemiddleware_5.1.0_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/bug-1766731-3b29192cfeb77964.yaml @ 245c91f2e3d499498e5f0edd30c23504cda9d111

- [`bug 1766731 <https://bugs.launchpad.net/keystonemiddleware/+bug/1766731>`_]
  Keystonemiddleware now supports system scoped tokens. When a system-scoped
  token is parsed by auth_token middleware, it will set the
  ``OpenStack-System-Scope`` header accordingly.


.. _keystonemiddleware_5.0.0:

5.0.0
=====

.. _keystonemiddleware_5.0.0_New Features:

New Features
------------

.. releasenotes/notes/bug-1695038-2cbedcabf8ecc057.yaml @ e83bd0bc3c7973e45b677c1c7007770e3f4873b4

- [`bug 1695038 <https://bugs.launchpad.net/keystonemiddleware/+bug/1695038>`_] The use_oslo_messaging configuration option is added for services such as Swift, which need the audit middleware to use the local logger instead of the oslo.messaging notifier regardless of whether the oslo.messaging package is present or not. Leave this option set to its default True value to keep the previous behavior unchanged - the audit middleware will use the oslo.messaging notifier if the oslo.messaging package is present, and the local logger otherwise. Services that rely on the local logger for audit notifications must set this option to False.


.. _keystonemiddleware_5.0.0_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/bug-1747655-6e563d9317bb0f13.yaml @ d3352ff422db6ba6a5e7bd4f7220af0d97efd0ac

- [`bug/1747655 <https://bugs.launchpad.net/keystonemiddleware/+bug/1747655>`_]
  When keystone is temporarily unavailable, keystonemiddleware correctly
  sends a 503 response to the HTTP client but was not identifying which
  service was down, leading to confusion on whether it was keystone or the
  service using keystonemiddleware that was unavailable. This change
  identifies keystone in the error response.


.. _keystonemiddleware_5.0.0_Other Notes:

Other Notes
-----------

.. releasenotes/notes/remove_kwargs_to_fetch_token-20e3451ed192ab6a.yaml @ 8e9255d56d2da16a7fec4f57e28246bb5b9cb713

- The ``kwargs_to_fetch_token`` setting was removed from the ``BaseAuthProtocol`` class. Implementations of auth_token now assume kwargs will be passed to the ``fetch_token`` method.

