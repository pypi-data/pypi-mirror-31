"""Async I/O Future utilities."""
import asyncio
import collections
import typing
from collections import deque
from functools import singledispatch
from typing import Any, Awaitable, Callable, Deque, Optional, Type, TypeVar
from weakref import WeakSet

__all__ = [
    'FlowControlEvent',
    'FlowControlQueue',
    'done_future',
    'maybe_async',
    'stampede',
    'notify',
]

_T = TypeVar('_T')


class StampedeWrapper:
    fut: asyncio.Future = None

    def __init__(self,
                 fun: Callable,
                 *args: Any,
                 loop: asyncio.AbstractEventLoop = None,
                 **kwargs: Any) -> None:
        self.fun = fun
        self.args = args
        self.kwargs = kwargs
        self.loop = loop

    async def __call__(self) -> Any:
        fut = self.fut
        if fut is None:
            fut = self.fut = asyncio.Future(loop=self.loop)
            try:
                result = await self.fun(*self.args, **self.kwargs)
                fut.set_result(result)
            except asyncio.CancelledError:
                fut.cancel()
                raise
            finally:
                self.fut = None
            return result
        else:
            if fut.done():
                return fut.result()
            return await fut


class stampede:
    """Descriptor for cached async operations providing stampede protection.

    See also thundering herd problem.

    Adding the decorator to an async callable method:

    Examples:
        Here's an example coroutine method connecting a network client:

        .. sourcecode:: python

            class Client:

                @stampede
                async def maybe_connect(self):
                    await self._connect()

                async def _connect(self):
                    return Connection()

        In the above example, if multiple coroutines call ``maybe_connect``
        at the same time, then only one of them will actually perform the
        operation. The rest of the coroutines will wait for the result,
        and return it once the first caller returns.
    """

    def __init__(self, fget: Callable, *, doc: str = None) -> None:
        self.__get = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__

    def __get__(self, obj: Any, type: Type = None) -> Any:
        if obj is None:
            return self
        try:
            w = obj.__dict__[self.__name__]
        except KeyError:
            w = obj.__dict__[self.__name__] = StampedeWrapper(self.__get, obj)
        return w


def done_future(result: Any = None, *,
                loop: asyncio.AbstractEventLoop = None) -> asyncio.Future:
    """Return :class:`asyncio.Future` that is already evaluated."""
    f = (loop or asyncio.get_event_loop()).create_future()
    f.set_result(result)
    return f


@singledispatch
async def maybe_async(res: Any) -> Any:
    """Await future if argument is Awaitable.

    Examples:
        >>> await maybe_async(regular_function(arg))
        >>> await maybe_async(async_function(arg))
    """
    return res


# XXX In Py3.7: register does not work with typing.Awaitable
@maybe_async.register(collections.Awaitable)
async def _(res: Awaitable) -> Any:
    return await res


class FlowControlEvent:
    """Manage flow control :class:`FlowControlQueue` instances.

    The FlowControlEvent manages flow in one or many queue instances
    at the same time.

    To flow control queues, first create the shared event::

        >>> flow_control = FlowControlEvent()

    Then pass that shared event to the queues that should be managed by it::

        >>> q1 = FlowControlQueue(maxsize=1, flow_control=flow_control)
        >>> q2 = FlowControlQueue(flow_control=flow_control)

    If you want the contents of the queue to be cleared when flow is resumed,
    then specify that by using the ``clear_on_resume`` flag::

        >>> q3 = FlowControlQueue(clear_on_resume=True,
        ...                       flow_control=flow_control)

    To suspend production into queues, use ``flow_control.suspend``::

        >>> flow_control.suspend()

    While the queues are suspend, any producer attempting to send something
    to the queue will hang until flow is resumed.

    To resume production into queues, use ``flow_control.resume``::

        >>> flow_control.resume()

    Notes:
        In Faust queues are managed by the ``app.flow_control`` event.
    """

    if typing.TYPE_CHECKING:
        _queues: WeakSet['FlowControlQueue']
    _queues = None

    def __init__(self, *,
                 initially_suspended: bool = True,
                 loop: asyncio.AbstractEventLoop = None) -> None:
        self.loop = loop or asyncio.get_event_loop()
        self._resume = asyncio.Event(loop=self.loop)
        self._suspend = asyncio.Event(loop=self.loop)
        if initially_suspended:
            self._suspend.set()
        self._queues = WeakSet()

    def manage_queue(self, queue: 'FlowControlQueue') -> None:
        """Add :class:`FlowControlQueue` to be cleared on resume."""
        self._queues.add(queue)

    def suspend(self) -> None:
        """Suspend production into queues managed by this event."""
        self._resume.clear()
        self._suspend.set()

    def is_active(self) -> bool:
        return not self._suspend.is_set()

    def resume(self) -> None:
        """Resume production into queues managed by this event."""
        self._suspend.clear()
        self._resume.set()
        self.clear()

    def clear(self) -> None:
        for queue in self._queues:
            queue.clear()

    async def acquire(self) -> None:
        """Wait until flow control is resumed."""
        if self._suspend.is_set():
            print('WAITING FOR RESUME')
            import traceback
            traceback.print_stack()
            await self._resume.wait()


class FlowControlQueue(asyncio.Queue):
    """:class:`asyncio.Queue` managed by :class:`FlowControlEvent`.

    See Also:
        :class:`FlowControlEvent`.
    """

    def __init__(self, maxsize: int = 0,
                 *,
                 flow_control: FlowControlEvent = None,
                 clear_on_resume: bool = False,
                 **kwargs: Any) -> None:
        self._flow_control = flow_control
        self._clear_on_resume = clear_on_resume
        if self._clear_on_resume:
            self._flow_control.manage_queue(self)
        super().__init__(maxsize, **kwargs)

    def clear(self) -> None:
        self._queue.clear()  # type: ignore

    async def put(self, value: _T) -> None:  # type: ignore
        await self._flow_control.acquire()
        await super().put(value)


class ThrowableQueue(FlowControlQueue):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._errors: Deque[BaseException] = deque()

    @typing.no_type_check
    async def get(self) -> _T:
        if self._errors:
            raise self._errors.popleft()
        return await super().get()

    def empty(self) -> bool:
        return super().empty() and not self._errors

    def clear(self) -> None:
        self._queue.clear()  # type: ignore
        self._errors.clear()

    def get_nowait(self) -> _T:
        if self._errors:
            raise self._errors.popleft()
        return super().get_nowait()

    async def throw(self, exc: BaseException) -> None:
        waiters = self._getters  # type: ignore
        while waiters:
            waiter = waiters.popleft()
            if not waiter.done():
                waiter.set_exception(exc)
                break
        else:
            self._errors.append(exc)


def notify(fut: Optional[asyncio.Future], result: Any = None) -> None:
    # can be used to turn a Future into a lockless, single-consumer condition,
    # for multi-consumer use asyncio.Condition
    if fut is not None and not fut.done():
        fut.set_result(result)
