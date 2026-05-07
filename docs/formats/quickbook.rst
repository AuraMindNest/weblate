.. _quickbook:

QuickBook files
---------------

.. note::

   QuickBook support is provided by the Boost Weblate fork. Upstream Weblate
   releases may not include this format.

QuickBook (``.qbk``) is a markup language used in Boost documentation. This
Weblate build registers :guilabel:`QuickBook file` as a monolingual
:ref:`ConvertFormat <bimono>` handler: translatable strings are extracted into
gettext PO stores and merged back into QuickBook sources using a built-in parser
(:mod:`weblate.utils.quickbook`).

There is **no** external converter binary (such as ``po4a``) required for
QuickBook in this fork—only Python dependencies from the main ``weblate``
package install.

Typical component setup
+++++++++++++++++++++++

+--------------------------------+-------------------------------------+
| Typical Weblate :ref:`component`                                     |
+================================+=====================================+
| File mask                      | ``path/*.qbk``                      |
+--------------------------------+-------------------------------------+
| Monolingual base language file | ``path/en.qbk``                     |
+--------------------------------+-------------------------------------+
| Template for new translations  | Same as base language file          |
+--------------------------------+-------------------------------------+
| File format                    | QuickBook file                      |
+--------------------------------+-------------------------------------+
