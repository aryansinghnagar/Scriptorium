#!/usr/bin/env python3
"""
Ars Arcanum GTK 3 Background Worker Engine (scripts/lib/ui_gtk3/workers.py)
==========================================================================
Provides async thread execution and GLib main loop event marshalling.
"""

import logging
import threading
from collections.abc import Callable
from typing import Any

from lib.ui_gtk3.common import HAS_GTK, GLib

logger = logging.getLogger("arcanum.ui_gtk3.workers")


class WorkerMixin:
    """Async background worker dispatching mixin for GTK windows."""

    def _start_worker(self, target_fn: Callable[..., Any], *args: Any, on_done: Callable[[], Any] | None = None, **kwargs: Any) -> None:
        """Runs a blocking task on a background daemon thread with progress feedback."""
        self._show_progress()

        call_args = kwargs.pop("args") if "args" in kwargs and isinstance(kwargs["args"], (tuple, list)) else args

        def _runner():
            try:
                target_fn(*call_args, **kwargs)
            except Exception as e:
                logger.error("Background task error: %s", e, exc_info=True)
            finally:
                if HAS_GTK and GLib is not None:
                    GLib.idle_add(self._hide_progress)
                    if on_done:
                        GLib.idle_add(on_done)

        thread = threading.Thread(target=_runner, daemon=True)
        thread.start()

    def _show_progress(self) -> None:
        """Shows pulse progress bar and starts pulsing timer."""
        if not HAS_GTK or not hasattr(self, "_progress_bar"):
            return
        self._progress_bar.show()
        if not getattr(self, "_pulse_timer_id", None) and GLib is not None:
            self._pulse_timer_id = GLib.timeout_add(80, self._pulse_tick)

    def _hide_progress(self) -> None:
        """Hides pulse progress bar and stops timer."""
        if not HAS_GTK or not hasattr(self, "_progress_bar"):
            return
        self._progress_bar.hide()
        timer_id = getattr(self, "_pulse_timer_id", None)
        if timer_id and GLib is not None:
            GLib.source_remove(timer_id)
            self._pulse_timer_id = None

    def _pulse_tick(self) -> bool:
        """Advances one pulse step on the progress bar."""
        if hasattr(self, "_progress_bar"):
            self._progress_bar.pulse()
        return True
