Configuration file
==================

Taika features configuration using INI files, since Python has builtin support
for it (via `configparser`). Here you will find the reference for the
configuration file.

The INI files are dividided into non-nestable sections, so here we will divide
the options in sections too.

If you are in doubt about what means "dangling-list", "section" or "dict" when
we specify the types of the configuration options, check the document :doc:`conf_types`.


``[taika]``
-----------

This section holds all the "global" configuration.

.. data:: extensions (dangling-list)

   A list of extensions to use.

   E.g.::

      [taika]
      extensions =
         taika.ext.rst
         taika.ext.permalinks


.. data:: extensions_paths (dangling-list)

   A list of paths where extensions live. This paths will be added to the ``sys.path`` in order to
   make the extensions inside it discoverable.

   E.g.::

      [taika]
      extensions_paths =
         ./extensions
         ./plugins
         ./_extensions
         /.extensions
         ~/.extensions
