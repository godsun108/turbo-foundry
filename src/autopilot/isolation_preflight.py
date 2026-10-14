"""Offline POSIX filesystem preflight for a privileged SQLite state store.

Necessary checks only: a successful result does NOT prove process isolation.
Never fixes permissions, creates files, or accesses provider credentials.
"""
from dataclasses import dataclass
import os
from pathlib import Path
import stat


@dataclass(frozen=True)
class IsolationPreflight:
    safe_to_review: bool
    reasons: tuple[str, ...]


def check_sqlite_isolation(db_path: str, *, expected_uid: int | None = None) -> IsolationPreflight:
    """Inspect the state DB and its parent without following symlinks.

    Requires 0600-or-tighter regular DB file and 0700-or-tighter parent.
    Only applicable to POSIX deployments; no changes are made.
    """
    reasons = []
    if os.name != "posix":
        return IsolationPreflight(False, ("non_posix_platform",))
    if not isinstance(db_path, str) or not db_path.strip():
        return IsolationPreflight(False, ("invalid_path",))
    if expected_uid is not None and (type(expected_uid) is not int or expected_uid < 0):
        return IsolationPreflight(False, ("invalid_expected_uid",))
    path = Path(db_path).absolute()
    try:
        file_stat = path.lstat()
        parent_stat = path.parent.lstat()
    except OSError:
        return IsolationPreflight(False, ("state_path_unavailable",))
    if not stat.S_ISREG(file_stat.st_mode):
        reasons.append("state_not_regular_file")
    if not stat.S_ISDIR(parent_stat.st_mode):
        reasons.append("parent_not_directory")
    if file_stat.st_mode & 0o077:
        reasons.append("state_group_or_other_access")
    if parent_stat.st_mode & 0o077:
        reasons.append("parent_group_or_other_access")
    if expected_uid is not None:
        if file_stat.st_uid != expected_uid:
            reasons.append("state_owner_mismatch")
        if parent_stat.st_uid != expected_uid:
            reasons.append("parent_owner_mismatch")
    for suffix in ("-wal", "-shm", "-journal"):
        sidecar = Path(str(path) + suffix)
        try:
            info = sidecar.lstat()
        except FileNotFoundError:
            continue
        except OSError:
            reasons.append("sidecar_unavailable")
            continue
        if not stat.S_ISREG(info.st_mode):
            reasons.append("sidecar_not_regular_file")
        if info.st_mode & 0o077:
            reasons.append("sidecar_group_or_other_access")
        if expected_uid is not None and info.st_uid != expected_uid:
            reasons.append("sidecar_owner_mismatch")
    return IsolationPreflight(not reasons, tuple(sorted(set(reasons))))
