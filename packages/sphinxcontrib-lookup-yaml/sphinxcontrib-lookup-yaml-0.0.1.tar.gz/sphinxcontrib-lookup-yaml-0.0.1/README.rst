sphinxcontrib-lookup-yaml
================================================================================

This Sphinx extension adds directive for looking up values from YAML files.
Values are inserted to document as `literal_block` nodes.

Usage
--------------------------------------------------------------------------------

Get value from key `test_var1`::

   .. lookup-yaml:: source.yml

      test_var1

Get element from array in `test_var1`::

   .. lookup-yaml:: source.yml

      test_var1
      2

Get value from key `test_subvar1` from dictionary `test_var1`::

   .. lookup-yaml:: source.yml

      test_var1
      test_subvar1

Directives
--------------------------------------------------------------------------------

lookup-yaml
   Lookup YAML value. First value is source file with YAML. Contents are newline
   separated keys to value.

Options
--------------------------------------------------------------------------------

lookup_yaml_root
   Look for YAML files relatively to this directory.

   **DEFAULT**: ..

Installing
--------------------------------------------------------------------------------

Issue command:

``pip install sphinxcontrib-lookup-yaml``

And add extension in your project's ``conf.py``::

   extensions = ['sphinxcontrib.lookup_yaml']
