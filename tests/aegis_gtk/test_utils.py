"""
Tests for aegis_gtk.utils module.

Note: Some functions require a running GTK main loop and are tested
with mock objects or simplified tests.
"""

import pytest
import threading
import time


class TestRunAsync:
    """Tests for the run_async decorator."""

    def test_run_async_returns_thread(self):
        """Verify run_async returns a thread object."""
        from aegis_gtk.utils import run_async

        @run_async
        def sample_func():
            pass

        result = sample_func()

        assert isinstance(result, threading.Thread)

    def test_run_async_thread_is_daemon(self):
        """Verify run_async creates daemon threads."""
        from aegis_gtk.utils import run_async

        @run_async
        def sample_func():
            pass

        thread = sample_func()

        assert thread.daemon is True

    def test_run_async_executes_function(self):
        """Verify the decorated function actually runs."""
        from aegis_gtk.utils import run_async

        result = []

        @run_async
        def append_value():
            result.append(42)

        thread = append_value()
        thread.join(timeout=1)

        assert result == [42]

    def test_run_async_passes_arguments(self):
        """Verify arguments are passed to the function."""
        from aegis_gtk.utils import run_async

        result = []

        @run_async
        def append_values(a, b, c=None):
            result.extend([a, b, c])

        thread = append_values(1, 2, c=3)
        thread.join(timeout=1)

        assert result == [1, 2, 3]

    def test_run_async_preserves_function_name(self):
        """Verify functools.wraps preserves metadata."""
        from aegis_gtk.utils import run_async

        @run_async
        def my_named_function():
            """My docstring."""
            pass

        assert my_named_function.__name__ == "my_named_function"
        assert my_named_function.__doc__ == "My docstring."


class TestRunInThread:
    """Tests for run_in_thread function."""

    def test_run_in_thread_returns_thread(self):
        """Verify run_in_thread returns a thread."""
        from aegis_gtk.utils import run_in_thread

        def sample():
            pass

        thread = run_in_thread(sample)

        assert isinstance(thread, threading.Thread)

    def test_run_in_thread_is_daemon(self):
        """Verify threads are daemon threads."""
        from aegis_gtk.utils import run_in_thread

        def sample():
            pass

        thread = run_in_thread(sample)

        assert thread.daemon is True

    def test_run_in_thread_executes(self):
        """Verify function executes in thread."""
        from aegis_gtk.utils import run_in_thread

        result = []

        def append():
            result.append("done")

        thread = run_in_thread(append)
        thread.join(timeout=1)

        assert result == ["done"]

    def test_run_in_thread_with_args(self):
        """Verify args and kwargs are passed."""
        from aegis_gtk.utils import run_in_thread

        result = []

        def store(a, b, key=None):
            result.extend([a, b, key])

        thread = run_in_thread(store, "x", "y", key="z")
        thread.join(timeout=1)

        assert result == ["x", "y", "z"]


class TestAsyncResult:
    """Tests for AsyncResult class."""

    def test_async_result_initial_state(self):
        """Test initial state of AsyncResult."""
        from aegis_gtk.utils import AsyncResult

        result = AsyncResult()

        assert result.value is None
        assert result.error is None
        assert result.completed.is_set() is False

    def test_async_result_set_value(self):
        """Test setting a value."""
        from aegis_gtk.utils import AsyncResult

        result = AsyncResult()
        result.set_value(42)

        assert result.value == 42
        assert result.completed.is_set() is True

    def test_async_result_set_error(self):
        """Test setting an error."""
        from aegis_gtk.utils import AsyncResult

        result = AsyncResult()
        error = ValueError("test error")
        result.set_error(error)

        assert result.error is error
        assert result.completed.is_set() is True

    def test_async_result_wait(self):
        """Test waiting for result."""
        from aegis_gtk.utils import AsyncResult

        result = AsyncResult()

        # Should timeout when not completed
        completed = result.wait(timeout=0.01)
        assert completed is False

        # Should return immediately when completed
        result.set_value("done")
        completed = result.wait(timeout=0.01)
        assert completed is True

    def test_async_result_get_value(self):
        """Test getting the value."""
        from aegis_gtk.utils import AsyncResult

        result = AsyncResult()
        result.set_value("test_value")

        assert result.get() == "test_value"

    def test_async_result_get_raises_error(self):
        """Test get raises stored exception."""
        from aegis_gtk.utils import AsyncResult

        result = AsyncResult()
        result.set_error(ValueError("test error"))

        with pytest.raises(ValueError, match="test error"):
            result.get()

    def test_async_result_threaded_usage(self):
        """Test typical threaded usage pattern."""
        from aegis_gtk.utils import AsyncResult

        result = AsyncResult()

        def background_work():
            time.sleep(0.05)
            result.set_value("completed")

        thread = threading.Thread(target=background_work)
        thread.start()

        value = result.get(timeout=1)
        assert value == "completed"


class TestIdleAdd:
    """Tests for idle_add function.

    Note: These tests verify the function signature and basic behavior.
    Full GTK main loop testing would require more complex setup.
    """

    def test_idle_add_accepts_function(self):
        """Verify idle_add accepts a callable."""
        from aegis_gtk.utils import idle_add

        # This will schedule but won't run without main loop
        source_id = idle_add(lambda: None)

        assert isinstance(source_id, int)
        assert source_id > 0

    def test_idle_add_accepts_args(self):
        """Verify idle_add accepts arguments."""
        from aegis_gtk.utils import idle_add

        source_id = idle_add(lambda x, y: None, 1, 2)

        assert isinstance(source_id, int)


class TestTimeoutAdd:
    """Tests for timeout_add function."""

    def test_timeout_add_returns_source_id(self):
        """Verify timeout_add returns a source ID."""
        from aegis_gtk.utils import timeout_add

        source_id = timeout_add(1000, lambda: False)

        assert isinstance(source_id, int)
        assert source_id > 0

    def test_timeout_add_with_args(self):
        """Verify timeout_add accepts arguments."""
        from aegis_gtk.utils import timeout_add

        source_id = timeout_add(1000, lambda x: False, "arg")

        assert isinstance(source_id, int)


class TestTimeoutAddSeconds:
    """Tests for timeout_add_seconds function."""

    def test_timeout_add_seconds_returns_source_id(self):
        """Verify timeout_add_seconds returns a source ID."""
        from aegis_gtk.utils import timeout_add_seconds

        source_id = timeout_add_seconds(1, lambda: False)

        assert isinstance(source_id, int)
        assert source_id > 0


class TestDebounce:
    """Tests for debounce decorator.

    Note: Full debounce testing requires GTK main loop.
    These tests verify basic decorator behavior.
    """

    def test_debounce_returns_callable(self):
        """Verify debounce returns a callable."""
        from aegis_gtk.utils import debounce

        @debounce(100)
        def my_func():
            pass

        assert callable(my_func)

    def test_debounce_preserves_name(self):
        """Verify functools.wraps preserves metadata."""
        from aegis_gtk.utils import debounce

        @debounce(100)
        def my_named_func():
            """My doc."""
            pass

        assert my_named_func.__name__ == "my_named_func"
        assert my_named_func.__doc__ == "My doc."


class TestThrottle:
    """Tests for throttle decorator.

    Note: Full throttle testing requires GTK main loop.
    These tests verify basic decorator behavior.
    """

    def test_throttle_returns_callable(self):
        """Verify throttle returns a callable."""
        from aegis_gtk.utils import throttle

        @throttle(100)
        def my_func():
            pass

        assert callable(my_func)

    def test_throttle_preserves_name(self):
        """Verify functools.wraps preserves metadata."""
        from aegis_gtk.utils import throttle

        @throttle(100)
        def my_throttled_func():
            """Throttle doc."""
            pass

        assert my_throttled_func.__name__ == "my_throttled_func"
        assert my_throttled_func.__doc__ == "Throttle doc."

    def test_throttle_first_call_immediate(self):
        """Verify first call executes immediately."""
        from aegis_gtk.utils import throttle

        calls = []

        @throttle(1000)  # Long throttle
        def track_call():
            calls.append(time.time())

        # First call should be immediate
        track_call()

        assert len(calls) == 1
