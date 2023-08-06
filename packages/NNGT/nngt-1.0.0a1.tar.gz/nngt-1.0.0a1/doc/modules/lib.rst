==========
Lib module
==========

Tools for the other modules.

.. warning::
    These tools have been designed primarily for internal use throughout the
    library and often work only in very specific situations (e.g.
    :func:`find_idx_nearest` works only on sorted arrays), so make sure you
    read their doc carefully before using them.


Content
=======

.. autosummary::

    nngt.lib.InvalidArgument
    nngt.lib.custom
    nngt.lib.decorate
    nngt.lib.delta_distrib
    nngt.lib.deprecated
    nngt.lib.find_idx_nearest
    nngt.lib.gaussian_distrib
    nngt.lib.graph_tool_check
    nngt.lib.is_integer
    nngt.lib.lin_correlated_distrib
    nngt.lib.log_correlated_distrib
    nngt.lib.lognormal_distrib
    nngt.lib.mpi_barrier
    nngt.lib.mpi_checker
    nngt.lib.mpi_random
    nngt.lib.nonstring_container
    nngt.lib.not_implemented
    nngt.lib.num_mpi_processes
    nngt.lib.on_master_process
    nngt.lib.seed
    nngt.lib.uniform_distrib


Details
=======

.. automodule:: nngt.lib
