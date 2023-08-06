LIGO Follow-up Advocate Tools
=============================

| **Build** | **Test** |
| :-: | :-: | :-: |
| [![build status](https://git.ligo.org/emfollow/ligo-followup-advocate/badges/master/build.svg)](https://git.ligo.org/emfollow/ligo-followup-advocate/pipelines) | [![coverage report](https://git.ligo.org/emfollow/ligo-followup-advocate/badges/master/coverage.svg)](https://emfollow.docs.ligo.org/ligo-followup-advocate/) |

To install
----------

The easiest way to install `ligo-followup-advocate`, is with `pip`:

    pip install --user git+https://git.ligo.org/emfollow/ligo-followup-advocate.git

To upgrade
----------

Once you have installed the package, to check for and install updates, run the
following command:

    pip install --user --upgrade --no-deps git+https://git.ligo.org/emfollow/ligo-followup-advocate.git

Example
-------

`ligo-followup-advocate` provides a single command to draft a GCN Circular
skeleton. Pass it the authors and the GraceDB ID as follows:

    ligo-followup-advocate compose \
        'A. Einstein (IAS)' 'S. Hawking (Cambridge)' \
        'I. Newton (Cambridge)' 'Data (Starfleet)' \
        'G184098'

Optionally, you can have the program open the draft in your default mail client
by passing it the `--mailto` option.

For a list of other supported commands, run:

    ligo-followup-advocate --help

For further options for composing circulars, run:

    ligo-followup-advocate compose --help

To develop
----------

To participate in development, clone the git repository:

    git clone git@git.ligo.org:emfollow/ligo-followup-advocate.git

See also
--------

See also the [FollowupAdvocates page][1] in the EM Follow-up Wiki.



[1]: https://wiki.ligo.org/Bursts/EMFollow/FollowupAdvocates
