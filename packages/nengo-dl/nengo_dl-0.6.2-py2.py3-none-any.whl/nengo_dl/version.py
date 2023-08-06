"""We use semantic versioning (see http://semver.org/).
Additionally, '.dev0' will be added to the version unless the code base
represents a release version. Commits for which the version doesn't have
'.dev0' should be git tagged with the version.
"""

import warnings

name = "nengo-dl"
version_info = (0, 6, 2)  # (major, minor, patch)
dev = False

version = "{v}{dev}".format(v='.'.join(str(v) for v in version_info),
                            dev='.dev0' if dev else '')

# check nengo version
try:
    from nengo.version import version_info as nengo_version

    minimum_nengo_version = (2, 7, 0)
    latest_nengo_version = (2, 7, 0)
    if nengo_version < minimum_nengo_version:  # pragma: no cover
        raise ValueError(
            "`nengo_dl` does not support `nengo` version %s. Upgrade "
            "with 'pip install --upgrade --no-deps nengo'." %
            (nengo_version,))
    elif nengo_version > latest_nengo_version:  # pragma: no cover
        warnings.warn(
            "This version of `nengo_dl` has not been tested with your `nengo` "
            "version %s. The latest fully supported version is %s" %
            (nengo_version, latest_nengo_version))
except ImportError:
    # nengo not installed, can't check version
    pass
