"""Watch a .env file for changes and re-encrypt automatically."""

import time
import os
from pathlib import Path
from typing import Callable, Optional


def _get_mtime(path: str) -> Optional[float]:
    """Return the modification time of a file, or None if it doesn't exist."""
    try:
        return os.path.getmtime(path)
    except FileNotFoundError:
        return None


def watch_env_file(
    env_path: str,
    on_change: Callable[[str], None],
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
) -> None:
    """
    Poll *env_path* for modifications and call *on_change* with the path
    whenever the file changes.

    Args:
        env_path:       Path to the .env file to watch.
        on_change:      Callback invoked with the file path on each change.
        interval:       Polling interval in seconds (default 1.0).
        max_iterations: Stop after this many poll cycles (None = run forever).
                        Useful for testing.
    """
    last_mtime = _get_mtime(env_path)
    iterations = 0

    while True:
        if max_iterations is not None and iterations >= max_iterations:
            break

        time.sleep(interval)
        current_mtime = _get_mtime(env_path)

        if current_mtime is not None and current_mtime != last_mtime:
            last_mtime = current_mtime
            on_change(env_path)

        iterations += 1


def build_reencrypt_callback(
    vault_path: str,
    project: str,
    password: Optional[str] = None,
) -> Callable[[str], None]:
    """
    Return a callback that re-encrypts the .env file into *vault_path*
    whenever it is called.

    Args:
        vault_path: Destination path for the encrypted vault file.
        project:    Project name used to look up / store the key.
        password:   Optional password for password-based encryption.
    """
    from envault.vault import create_vault, save_vault
    from envault.keystore import retrieve_key, store_key
    from envault.audit import record_event

    def _callback(env_path: str) -> None:
        try:
            key = retrieve_key(project)
        except KeyError:
            key = None

        vault_data, used_key = create_vault(
            env_path=env_path,
            key=key,
            password=password,
        )

        if key is None and used_key is not None:
            store_key(project, used_key)

        save_vault(vault_data, vault_path)
        record_event("watch_reencrypt", project=project, vault=vault_path)

    return _callback
