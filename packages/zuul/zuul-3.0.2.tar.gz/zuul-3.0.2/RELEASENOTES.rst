====
zuul
====

.. _zuul_3.0.1:

3.0.1
=====

.. _zuul_3.0.1_New Features:

New Features
------------

.. releasenotes/notes/git-remote-refs-71bd2fc2bb05155d.yaml @ b'88f796435d304a05fb7d9ee08798fa287e818e9f'

- Git repositories will have a ``origin`` remote with refs pointing to the
  previous change in the speculative state.
  
  This allows jobs to determine the commits that are part of a change, which
  was not possible before. The remote URL is set to a bogus value which
  won't work with git commands that need to talk to the remote repository.

.. releasenotes/notes/postgres-ae4f8594d0f4b256.yaml @ b'68727f6c0262181e4ba70b0ec757823c1847bbeb'

- PostgreSQL is now officially supported as database backend.
  See :attr:`<sql connection>` on how to configure database connections.

.. releasenotes/notes/tenant-from-script-e28d736001db5365.yaml @ b'109766afb25c42f4bce840a050ea01d379228c4b'

- A new option for the scheduler
  :attr:`scheduler.tenant_config_script` can be used to tell Zuul to
  execute a script and read its yaml output as the tenants
  configuration. The option is exclusive with the
  :attr:`scheduler.tenant_config` option.


.. _zuul_3.0.1_Upgrade Notes:

Upgrade Notes
-------------

.. releasenotes/notes/version-table-prefix-c6a5e84851268f4d.yaml @ b'56fc36dd60062a00e10dfbc0c268595290cd6f98'

- The alembic version table is fixed to being prefixed too. This is necessary
  when using :attr:`<sql connection>.table_prefix`. However if you are
  already using ``table_prefix`` you will need to rename the table
  ``alembic_version`` to ``<prefix>alembic_version`` before starting Zuul.
  Otherwise zuul will try to create the tables again and fail. If you're not
  using ``table_prefix`` you can safely ignore this.


.. _zuul_3.0.1_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/role-checkouts-89632d2ff5eb8b78.yaml @ b'd0a3567221011eda22c9b42645887e5eb623e308'

- Zuul role repository checkouts now honor :attr:`job.override-checkout`.
  
  Previously, when a Zuul role was specified for a job, Zuul would
  usually checkout the master branch, unless that repository
  appeared in the dependency chain for a patch.  It will now follow
  the usual procedure for determining the branch to check out,
  including honoring :attr:`job.override-checkout` options.
  
  This may alter the behavior of currently existing jobs.  Depending
  on circumstances, you may need to set
  :attr:`job.override-checkout` or copy roles to other branches of
  projects.


.. _zuul_3.0.2:

3.0.2
=====

.. _zuul_3.0.2_New Features:

New Features
------------

.. releasenotes/notes/github-regex-status-26ddf3e3c91d182f.yaml @ b'0c3b8fb963e211c61ed378bdac33891f4312d061'

- The GitHub trigger status filter
  :value:`pipeline.trigger.<github source>.action.status` and pipeline
  requirements :attr:`pipeline.require.<github source>.status` now support
  regular expression matching.


.. _zuul_3.0.2_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/reporters-always-report-27702c27369176da.yaml @ b'1a03f7e689115b2fe56da9bf9edbba4ac859e50e'

- Story 2001441 is fixed. Failure by one Zuul reporter will not short
  circuit the reporting of other reporters. This ensures as much
  information as possible is reported for each change even if some
  failures occur. Note that the build set status is changed to 'ERROR'
  after the first failed reporter.

.. releasenotes/notes/zuul-changes-fix-6d1be83959d451ce.yaml @ b'559af7048bc8029cf120d09bb2ed0b74577bc28c'

- The zuul-changes.py script has been adapted to the new zuul-web api routes.

