from typing import TypeVar, Generic, Callable, Any
from reactivex.subject import ReplaySubject
from dataclasses import is_dataclass

State = TypeVar("State", bound=Any)


class StateMustBeADataClass(Exception):
    def __init__(self):
        pass

    def __iter__(self):
        yield "name", __class__.__name__


class Cubit(Generic[State]):
    _state: State
    _state_subject: ReplaySubject

    def __init__(self, initial_state: State):
        if not is_dataclass(initial_state):
            raise StateMustBeADataClass()
        self._state: State = initial_state
        self._state_subject: ReplaySubject = ReplaySubject(1)
        self._state_subject.on_next(self._state)

    @property
    def state(self) -> State:
        return self._state

    def emit(self, new_state: State):
        if not is_dataclass(new_state):
            raise StateMustBeADataClass()
        if new_state == self._state:
            return
        self._state = new_state
        self._state_subject.on_next(new_state)

    def subscribe(self, callback: Callable[[State], Any]):
        disposable = self._state_subject.subscribe(callback)

        async def unsubscribe():
            disposable.dispose()

        return unsubscribe

    def dispose(self):
        self._state_subject.on_completed()
        self._state_subject.dispose()
