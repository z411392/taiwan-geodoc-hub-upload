from typing import TypeVar, Generic, Callable, Awaitable, Dict, Type, Any, Mapping
from reactivex.subject import ReplaySubject

Event = TypeVar("Event", bound=Any)
State = TypeVar("State", bound=Mapping[Any, Any])


class Bloc(Generic[Event, State]):
    _state: State
    _state_subject: ReplaySubject
    _handlers: Dict[Type[Event], Callable[[Event], Awaitable[State]]]

    def __init__(self, initial_state: State):
        self._state: State = initial_state
        self._state_subject: ReplaySubject = ReplaySubject(1)
        self._handlers: Dict[Type[Event], Callable[[Event], Awaitable[State]]] = {}
        self._state_subject.on_next(self._state)

    @property
    def state(self) -> State:
        return self._state

    def emit(self, new_state: State):
        if new_state == self._state:
            return
        self._state = new_state
        self._state_subject.on_next(new_state)
        return

    def on(
        self,
        event_type: Type[Event],
        handler: Callable[[Event], Awaitable[State]],
    ):
        self._handlers[event_type] = handler

    async def add(self, event: Event):
        handler = self._handlers.get(type(event))
        if not handler:
            return
        await handler(event)

    def subscribe(self, callback: Callable[[State], Any]):
        disposable = self._state_subject.subscribe(callback)

        async def unsubscribe():
            disposable.dispose()

        return unsubscribe

    def dispose(self):
        self._state_subject.on_completed()
        self._state_subject.dispose()
