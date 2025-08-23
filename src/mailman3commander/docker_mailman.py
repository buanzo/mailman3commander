"""Helper functions for running Mailman Core commands via Docker Compose.

These helpers wrap ``docker compose exec -T mailman-core`` invocations to
allow programmatic interaction with the Mailman CLI from Python. Each
function returns a tuple ``(stdout, stderr, returncode)`` allowing callers to
inspect the command result.
"""

from __future__ import annotations

import subprocess
from typing import Iterable, List, Tuple

CommandResult = Tuple[str, str, int]


def _run_mailman(args: List[str], input_data: str | None = None) -> CommandResult:
    """Run a Mailman command inside the ``mailman-core`` container.

    Parameters
    ----------
    args:
        Additional arguments for the ``mailman`` command.
    input_data:
        Optional string passed to ``stdin``. Useful for commands like
        ``addmembers`` that expect a list of addresses on standard input.
    """
    cmd = ["docker", "compose", "exec", "-T", "mailman-core", "mailman"] + args
    result = subprocess.run(
        cmd,
        input=input_data,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout, result.stderr, result.returncode


def list_lists() -> CommandResult:
    """List all available mailing lists.

    Returns
    -------
    (stdout, stderr, returncode):
        Output of ``mailman lists``.
    """

    return _run_mailman(["lists"])


def list_members(list_name: str) -> CommandResult:
    """List members of ``list_name``.

    Parameters
    ----------
    list_name:
        Fully qualified name of the mailing list.
    """

    return _run_mailman(["members", list_name])


def add_members(list_name: str, members: Iterable[str]) -> CommandResult:
    """Add ``members`` to ``list_name`` using ``mailman addmembers``.

    ``members`` should be an iterable of email addresses. They will be joined
    with newlines and passed to the command via ``stdin``.
    """

    data = "\n".join(members) + "\n"
    # The ``-`` tells Mailman to read addresses from standard input.
    return _run_mailman(["addmembers", list_name, "-"], input_data=data)

