.. highlight:: ini

Configuration types
===================

The default types of options that can be retrieved are listed in the :mod:`configparser`, at the
official Python documentation. Here we list only those added by us.

List
----

.. tip::

   **[Extension Authors]** You can easily retrieve them with ``getlist``.

List separated by line separators, can be a single element::

   option = element

or multiple elements::

   option =
      element_one
      element_two
      element_three


Dictionary
----------

.. tip::

   **[Extension Authors]** You can easily retrieve them with ``getdict``.

List where each line has one or more equal signs (``=``) to delimite key-value pairs. Each line can have more than
one "=", as we only will split by the first equal sign on the left::

   option = key=value

or::

   option =
      key = value
      key = value = sign  # The second equal sign is retained

