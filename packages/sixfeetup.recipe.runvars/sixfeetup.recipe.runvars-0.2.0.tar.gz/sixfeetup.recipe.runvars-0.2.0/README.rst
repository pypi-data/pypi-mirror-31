Introduction
************

This recipe can be used to populate a buildout_ part with variables whose values come from external commands.

Fetch your secrets from the environment when possible, not from managed source code. In our example below, we move them to LastPass, write them to an unmanaged file during the buildout, and read them from the environment during execution.

You can use this approach in order to keep credentials and other sensitive secrets out of the repository.

.. contents::

A short example::


  [sekrets]
  recipe = sixfeetup.recipe.runvars
  username = somedewd
  password = `lpass show --password somedewd@some.api.com`

Now you are free to use ``${sekrets:username}`` and ``${sekrets:password}`` in
other parts or templates as part of your buildout.

This is useful for populating environment variables as part of system
configuration, for example.

.. _buildout: http://buildout.org
