====
reno
====

.. _reno_2.2.0:

2.2.0
=====

.. _reno_2.2.0_New Features:

New Features
------------

.. releasenotes/notes/no-show-source-option-ee02766b26fe53be.yaml @ 33b135fe9a04dbaddc82f27f21f5955cbbefac02

- Add a ``--no-show-source`` option to the report command to skip
  including the note reference file names and SHA information
  in comments in the output. This restores the previous format of
  the output for cases where it is meant to be read by people directly,
  not just converted to HTML.

.. releasenotes/notes/report-title-option-f0875bfdbc54dd7b.yaml @ 371fb0ff768668624c93c4ae135f63854fdf6e2a

- Add a ``--title`` option to the report command.


.. _reno_2.2.1:

2.2.1
=====

.. _reno_2.2.1_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/avoid-clashing-uids-e84ffe8132ce996d.yaml @ 8b1a3c652747f2d70c2136642ad5e1875971a870

- Fix a problem caused by failing to process multiple files with the
  same UID portion of the filename. Ignore existing cases as long as
  there is a corrective patch to remove them. Prevent new cases from
  being introduced. See https://bugs.launchpad.net/reno/+bug/1688042
  for details.


.. _reno_2.6.0:

2.6.0
=====

.. _reno_2.6.0_New Features:

New Features
------------

.. releasenotes/notes/Enable-using-tempalte-file-be734d8698309409.yaml @ 247f3afddfe5169b28154d1e86fb4e06c5d8b834

- The ``--from-template`` flag was added to the release note creation command.
  This enables one to create a release note from a pre-defined template,
  which is useful when automating the creation of commits.


.. _reno_2.6.0_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/scanner-change-96682cb04fc66c0b.yaml @ 9d058ae097e6cfac079fdbabadfc4270c6297e7f

- A fix is included to ignore changes to a note file until the
  scanner encounters the git operation that adds the file. This
  ensures that if a file is modified on master when it should be
  modified on another branch the note is not erroneously
  incorporated into the notes for the next release from master.
  fixes `bug 1682796`_
  
  .. _bug 1682796: https://bugs.launchpad.net/neutron/+bug/1682796


.. _reno_2.3.0:

2.3.0
=====

.. _reno_2.3.0_New Features:

New Features
------------

.. releasenotes/notes/add-linter-ce0a861ade64baf2.yaml @ 06d6574d46091d48b9c78878cac04f639aec39cc

- Add a ``lint`` command for checking the contents and names of the
  release notes files against some basic validation rules.


.. _reno_2.3.0_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/log-levels-and-sphinx-161-6efe0d291718a657.yaml @ 2d0d05d3019376af6377f0d47e06ac5bea88c31e

- Sphinx 1.6.1 now interprets error and warning log messages as
  reasons to abort the build when strict mode is enabled. This
  release changes the log level for some calls that weren't really
  errors to begin with to avoid having Sphinx abort the build
  unnecessarily.


.. _reno_2.3.2:

2.3.2
=====

.. _reno_2.3.2_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/fix-delete-handling-55232c50b647aa57.yaml @ 5cefb37405522445e27cb5a396626c3bb4aa680d

- Correct a problem with handling deleted release notes that
  triggered a TypeError with a message like "Can't mix strings and
  bytes in path components"


.. _reno_2.1.0:

2.1.0
=====

.. _reno_2.1.0_New Features:

New Features
------------

.. releasenotes/notes/config-option-branch-name-re-8ecfe93195b8824e.yaml @ 10ccdda0eb8c1932dc4c8c2a66f46f0e7cf8bb0a

- Add a configuration option ``branch_name_re`` to hold a regular expression
  for choosing "interesting" branches when trying to automatically detect
  how far back the scanner should look. The default is ``stable/.+``, which
  works for the OpenStack practice of creating branches named after the
  stable series of releases.

.. releasenotes/notes/config-option-sections-9c68b070698e984a.yaml @ 081a4145e18c82acba877ee22c180b3428c773f6

- Add a configuration option ``sections`` to hold the list of
  permitted section identifiers and corresponding display names.
  This also determines the order in which sections are collated.

.. releasenotes/notes/custom-tag-versions-d02028b6d35db967.yaml @ 10ccdda0eb8c1932dc4c8c2a66f46f0e7cf8bb0a

- Add the ability to specify regular expressions to a define a
  customised versioning scheme for release tags and pre-release tags.
  
  By default this change supports the current versioning scheme used by
  OpenStack.
  
  To customise, update the config.yaml file with the appropriate values.
  For example, for tags with versions like ``v1.0.0`` and pre-release
  versions like ``v1.0.0rc1`` the following could be added to config.yaml::
  
    release_tag_re: 'v\d\.\d\.\d(rc\d+)?'
    pre_release_tag_re: '(?P<pre_release>rc\d+$)'

.. releasenotes/notes/include-working-copy-d0aed2e77bb095e6.yaml @ f8fc8f97ff20026582742e3e7838cdd0ed5cad68

- Include the local working copy when scanning the history of the
  current branch. Notes files must at least be staged to indicate
  that they will eventually be part of the history, but subsequent
  changes to the file do not need to also be staged to be seen.

.. releasenotes/notes/show-less-unreleased-802781a1a3bf110e.yaml @ 10ccdda0eb8c1932dc4c8c2a66f46f0e7cf8bb0a

- The scanner for the "current" branch (usually ``master``) now stops
  when it encounters the base of an earlier branch matching the
  ``branch_name_re`` config option. This results in less history
  appearing on the unreleased pages, while still actually showing
  the current series and any unreleased notes.

.. releasenotes/notes/show-note-filename-in-report-a1118c917588b58d.yaml @ b0ba2eeea5b816887ace3e72fe3beb2e3838e705

- The report output now includes debugging details with the filename
  and sha for the version of the content used to indicate where the
  content is from to assist with debugging formatting or content
  issues.


.. _reno_2.1.0_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/config-option-branch-name-re-8ecfe93195b8824e.yaml @ 10ccdda0eb8c1932dc4c8c2a66f46f0e7cf8bb0a

- Fixes the logic for determining how far back in history to look when
  scanning a given branch. Reno now looks for the base of the "previous"
  branch, as determined by looking at branches matching ``branch_name_re``
  in lexical order. This may not work if branches are created using
  version numbers as their names.


.. _reno_2.8.0:

2.8.0
=====

.. _reno_2.8.0_New Features:

New Features
------------

.. releasenotes/notes/unreleased-version-title-86751f52745fd3b7.yaml @ 187d586d5fdaba42d4e6b720ffbfa3b5530d4939

- Added configuration option ``unreleased_version_title`` with
  associated Sphinx directive argument to control whether to show
  the computed version number for changes that have not been
  tagged, or to show a static title string specified in the option
  value.


.. _reno_2.5.0:

2.5.0
=====

.. _reno_2.5.0_New Features:

New Features
------------

.. releasenotes/notes/flexible-formatting-31c8de2599d3637d.yaml @ bc3d1241dd842dcfb8797747b4083ba93ffd33cb

- Release notes entries may now be made up of single strings. This simplifies formatting for smaller notes, and eliminates a class of errors associated with escaping reStructuredText inside YAML lists.

.. releasenotes/notes/ignore-notes-option-9d0bde540fbcdf22.yaml @ f957e74ff96038e69f2ffaee69b1a5e3f0727380

- Add a new configuration option ``ignore_notes``. Setting the value
  to a list of filenames or UIDs for notes causes the reno scanner
  to ignore them.  It is most useful to set this when a note is
  edited on the wrong branch, making it appear to be part of a
  release that it is not.

.. releasenotes/notes/repodir-config-file-b6b8edc2975964fc.yaml @ ecd1a171bae4f101bfe956d8a22bc023fb0cc9d3

- reno will now scan for a ``reno.yaml`` file in the root repo directory if a
  ``config.yaml`` file does not exist in the releasenotes directory. This
  allows users to do away with the unnecessary ``notes`` subdirectory in the
  releasenotes directory.


.. _reno_2.9.0:

2.9.0
=====

.. _reno_2.9.0_New Features:

New Features
------------

.. releasenotes/notes/setuptools-integration-950bd8ab6d2970c7.yaml @ b7bb0f1e087046fee9ca8bd147fddbb58d5b1aa2

- Add a ``build_reno`` setuptools command that allows users to generate a
  release notes document and a reno cache file that can be used to build
  release notes documents without the full Git history present.

.. releasenotes/notes/stable-section-anchors-d99258b6df39c0fa.yaml @ 847f13a14abe5a1d7bd748ba39ea4d948dff150d

- Added explicitly calculated anchors to ensure section links are both
  unique and stable over time.


.. _reno_2.0.2:

2.0.2
=====

.. _reno_2.0.2_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/fix-branch-base-detection-95300805f26a0c15.yaml @ 10ccdda0eb8c1932dc4c8c2a66f46f0e7cf8bb0a

- Fix a problem with the way reno automatically detects the initial
  version in a branch that prevented it from including all of the
  notes associated with a release, especially if the branch was
  created at a pre-release version number.
  `Bug #1652092 <https://bugs.launchpad.net/reno/+bug/1652092>`__


.. _reno_2.0.0:

2.0.0
=====

.. _reno_2.0.0_Prelude:

Prelude
-------

.. releasenotes/notes/dulwich-rewrite-3a5377162d97402b.yaml @ 389d4672c8bab9197e9c1a6e429d4eb7d1f0849f

This release includes a significant rewrite of the internal logic of reno to access git data through the dulwich library instead of the git command line porcelain.


.. _reno_2.0.0_New Features:

New Features
------------

.. releasenotes/notes/add-config-file-e77084792c1dc695.yaml @ 389d4672c8bab9197e9c1a6e429d4eb7d1f0849f

- Reno now supports having a ``config.yaml`` file in your release notes
  directory. It will search for file in the directory specified by
  ``--rel-notes-dir`` and parse it. It will apply whatever options are
  valid for that particular command. If an option is not relevant to a
  particular sub-command, it will not attempt to apply them.

.. releasenotes/notes/branches-eol-bcafc2a007a1eb9f.yaml @ 389d4672c8bab9197e9c1a6e429d4eb7d1f0849f

- Explicitly allow reno to scan starting from a tag by specifying the
  tag where a branch name would otherwise be used.

.. releasenotes/notes/branches-eol-bcafc2a007a1eb9f.yaml @ 389d4672c8bab9197e9c1a6e429d4eb7d1f0849f

- Add logic to allow reno to detect a branch that has been marked as
  end-of-life using the OpenStack community's process of tagging the
  HEAD of a stable/foo branch foo-eol before deleting the
  branch. This means that references to "stable/foo" are translated
  to "foo-eol" when the branch does not exist, and that Sphinx
  directives do not need to be manually updated.

.. releasenotes/notes/default-repository-root-cli-85d23034bef81619.yaml @ c745d30c8b83db868783fa724d3f832206f9d8b3

- Set the default value of the reporoot argument for all command line programs to "." and make it an optional parameter.

.. releasenotes/notes/stop-scanning-branch-e5a8937c248acc99.yaml @ 6f6e7addfb7b1bda65efecb362fb206731bcab2e

- Automatically stop scanning branches at the point where they diverge from master. This avoids having release notes from older versions, that appear on master before the branch, from showing up in the versions from the branch. This logic is only applied to branches created from master.

.. releasenotes/notes/stop-scanning-branch-option-6a0156b183814d7f.yaml @ 7ee2a78a8a865980ed9a2f07be3f55211e5a90b3

- Add a new configuration option, stop_at_branch_base, to control whether or not the scanner stops looking for changes at the point where a branch diverges from master. The default is True, meaning that the scanner does stop. A false value means that versions that appear on master from a point earlier than when the branch was created will be included when scanning the branch for release notes.

.. releasenotes/notes/support-custom-template-0534a2199cfec44c.yaml @ 389d4672c8bab9197e9c1a6e429d4eb7d1f0849f

- Reno now supports to set through ``template`` attribute in
  ``config.yaml`` a custom template which will be used by reno new
  to create notes.

.. releasenotes/notes/support-edit-ec5c01ad6144815a.yaml @ 389d4672c8bab9197e9c1a6e429d4eb7d1f0849f

- Reno now enables with reno new ``--edit`` to create a note and edit it with
  your editor (defined with EDITOR environment variable).


.. _reno_2.1.2:

2.1.2
=====

.. _reno_2.1.2_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/fix-sphinxext-scanner-0aa012ada66db773.yaml @ 3387cfb3a69657a8a7e2e40eabbb56c514c797d4

- Fixes a problem with the sphinx extension that caused it to
  produce an error if it had a list of versions to include that were
  not within the set that seemed to be on the branch because of the
  branch-base detection logic. Now if a list of versions is
  included, the scan always includes the full history.


.. _reno_2.4.0:

2.4.0
=====

.. _reno_2.4.0_New Features:

New Features
------------

.. releasenotes/notes/ignore-null-merges-56b7a8ed9b20859e.yaml @ bd6fecc8587ee919eba78b9fd70a17e6a5ad510a

- By default, reno now ignores "null" merge commits that bring in
  tags from other threads. The new configuration option
  ``ignore_null_merges`` controls this behavior. Setting the flag to
  False restores the previous behavior in which the null-merge
  commits were traversed like any other merge commit.


.. _reno_2.4.0_Upgrade Notes:

Upgrade Notes
-------------

.. releasenotes/notes/ignore-null-merges-56b7a8ed9b20859e.yaml @ bd6fecc8587ee919eba78b9fd70a17e6a5ad510a

- The new configuration option ``ignore_null_merges`` causes the
  scanner to ignore merge commits with no changes when one of the
  parents being merged in has a release tag on it.


.. _reno_2.4.0_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/ignore-null-merges-56b7a8ed9b20859e.yaml @ bd6fecc8587ee919eba78b9fd70a17e6a5ad510a

- This release fixes a problem with the scanner that may have caused
  it to stop scanning a branch prematurely when the tag from another
  branch had been merged into the history.


.. _reno_2.4.1:

2.4.1
=====

.. _reno_2.4.1_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/null-merge-infinite-loop-670367094ad83e19.yaml @ a42a617350e36c0f09859c95ba89c64aa38009d2

- Remove an infinite loop in the traversal algorithm caused by some
  null-merge skip situations.


.. _reno_2.7.0:

2.7.0
=====

.. _reno_2.7.0_New Features:

New Features
------------

.. releasenotes/notes/add-closed-branch-config-options-8773caf240e4653f.yaml @ b9cf9a7371eec7f20089f51bbd12e78963a10960

- Adds new configuration options ``closed_branch_tag_re`` (to
  identify tags that replace branches that have been closed) and
  ``branch_name_prefix`` (a value to be added back to the closed
  branch tag to turn it into the original branch name.
  
  These options are used in OpenStack to support scanning the
  history of a branch based on the previous series branch, even
  after that previous series is closed by setting
  ``closed_branch_tag_re`` to ``(.+)-eol`` so that the series name
  in a value like ``"mitaka-eol"`` is extracted using the
  group. With ``branch_name_prefix`` set to ``"stable/"`` the tag
  ``mitaka-eol`` becomes the branch name ``stable/mitaka``.


.. _reno_2.7.0_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/add-closed-branch-config-options-8773caf240e4653f.yaml @ b9cf9a7371eec7f20089f51bbd12e78963a10960

- Fixes bug 1746076 so that scanning stable branches correctly
  includes the history of earlier closed stable branches.


.. _reno_2.1.1:

2.1.1
=====

.. _reno_2.1.1_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/allow-short-branch-names-61a35be55f04cea4.yaml @ 2e9cd7cfe53ae2a7c8b81dcc99a67114d410e382

- Fix a problem with branch references so that it is now possible to
  use a local tracking branch name when the branch only exists on
  the 'origin' remote. For example, this allows references to
  'stable/ocata' when there is no local branch with that name but
  there is an 'origin/stable/ocata' branch.


.. _reno_2.5.1:

2.5.1
=====

.. _reno_2.5.1_New Features:

New Features
------------

.. releasenotes/notes/reference-name-mangling-3c845ebf88af6944.yaml @ bbe3543f7855d8dab9ac2c445530d7a782bc1e6e

- The automatic branch name handling is updated so that if the
  reference points explicitly to the origin remote, but that remote
  isn't present (as it won't be when zuul configures the repo in
  CI), then the shortened form of the reference without the prefix
  is used instead. This allows explicit references to
  ``origin/stable/name`` to be translated to ``stable/name`` and
  find the expected branch.


.. _reno_2.3.1:

2.3.1
=====

.. _reno_2.3.1_Other Notes:

Other Notes
-----------

.. releasenotes/notes/optional-oslosphinx-55843a7f80a14e58.yaml @ e3dcbdd582b950504a17147b60e02904f3a5e8c8

- The oslosphinx dependency for building documentation is now optional. This breaks a build cycle between oslosphinx and reno.

