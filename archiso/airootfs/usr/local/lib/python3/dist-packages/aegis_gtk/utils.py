"""
Aegis GTK Utilities - Helper functions for Aegis applications.
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import GLib, Adw
import threading
from typing import Any, Optional
from collections.abc import Callable
from functools import wraps


def run_async(func: Callable) -> Callable:
    """Decorator to run a function in a background thread.

    The decorated function will run in a daemon thread.
    Use GLib.idle_add() inside the function to update UI.

    Example:
        @run_async
        def fetch_data():
            data = slow_network_call()
            GLib.idle_add(update_ui, data)
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread

    return wrapper


def run_in_thread(func: Callable, *args, **kwargs) -> threading.Thread:
    """Run a function in a background thread.

    Args:
        func: Function to run
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        The started thread
    """
    thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    return thread


def idle_add(func: Callable, *args) -> int:
    """Schedule a function to run on the main GTK thread.

    This is a convenience wrapper around GLib.idle_add().

    Args:
        func: Function to call
        *args: Arguments to pass to the function

    Returns:
        Source ID (can be used with GLib.source_remove())
    """
    if args:
        return GLib.idle_add(func, *args)
    return GLib.idle_add(func)


def timeout_add(interval_ms: int, func: Callable, *args) -> int:
    """Schedule a function to run after a delay.

    Args:
        interval_ms: Delay in milliseconds
        func: Function to call
        *args: Arguments to pass to the function

    Returns:
        Source ID (can be used with GLib.source_remove())
    """
    if args:
        return GLib.timeout_add(interval_ms, func, *args)
    return GLib.timeout_add(interval_ms, func)


def timeout_add_seconds(interval_sec: int, func: Callable, *args) -> int:
    """Schedule a function to run repeatedly at an interval.

    The function should return True to continue, False to stop.

    Args:
        interval_sec: Interval in seconds
        func: Function to call (should return bool)
        *args: Arguments to pass to the function

    Returns:
        Source ID (can be used with GLib.source_remove())
    """
    if args:
        return GLib.timeout_add_seconds(interval_sec, func, *args)
    return GLib.timeout_add_seconds(interval_sec, func)


def show_toast(overlay: Adw.ToastOverlay, message: str, timeout: int = 2):
    """Show a toast notification.

    Args:
        overlay: The Adw.ToastOverlay to show the toast in
        message: The message to display
        timeout: Duration in seconds (default 2)
    """
    toast = Adw.Toast(title=message)
    toast.set_timeout(timeout)
    overlay.add_toast(toast)


class AsyncResult:
    """A container for async operation results."""

    def __init__(self):
        self.value: Any = None
        self.error: Exception | None = None
        self.completed = threading.Event()

    def set_value(self, value: Any):
        self.value = value
        self.completed.set()

    def set_error(self, error: Exception):
        self.error = error
        self.completed.set()

    def wait(self, timeout: float | None = None) -> bool:
        """Wait for the result. Returns True if completed, False if timed out."""
        return self.completed.wait(timeout)

    def get(self, timeout: float | None = None) -> Any:
        """Wait for and return the result. Raises exception if one occurred."""
        self.wait(timeout)
        if self.error:
            raise self.error
        return self.value


def debounce(wait_ms: int):
    """Decorator to debounce function calls.

    Only the last call within the wait period will be executed.

    Args:
        wait_ms: Wait time in milliseconds

    Example:
        @debounce(300)
        def on_search_changed(text):
            # This will only run 300ms after the last call
            perform_search(text)
    """

    def decorator(func: Callable) -> Callable:
        timer_id = [None]  # Use list to allow modification in closure

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Cancel previous timer if exists
            if timer_id[0] is not None:
                GLib.source_remove(timer_id[0])

            # Set new timer
            def call_func():
                timer_id[0] = None
                func(*args, **kwargs)
                return False  # Don't repeat

            timer_id[0] = GLib.timeout_add(wait_ms, call_func)

        return wrapper

    return decorator


def throttle(wait_ms: int):
    """Decorator to throttle function calls.

    The function will be called at most once per wait period.

    Args:
        wait_ms: Minimum time between calls in milliseconds

    Example:
        @throttle(100)
        def on_slider_changed(value):
            # This will run at most every 100ms
            update_device(value)
    """

    def decorator(func: Callable) -> Callable:
        last_call = [0]
        pending_call = [None]

        @wraps(func)
        def wrapper(*args, **kwargs):
            import time

            now = time.time() * 1000

            if now - last_call[0] >= wait_ms:
                # Enough time has passed, call immediately
                last_call[0] = now
                func(*args, **kwargs)
            else:
                # Schedule for later if not already scheduled
                if pending_call[0] is None:

                    def delayed_call():
                        pending_call[0] = None
                        last_call[0] = time.time() * 1000
                        func(*args, **kwargs)
                        return False

                    remaining = wait_ms - (now - last_call[0])
                    pending_call[0] = GLib.timeout_add(int(remaining), delayed_call)

        return wrapper

    return decorator
