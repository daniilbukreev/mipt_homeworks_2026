import json
from datetime import UTC, datetime
from functools import wraps
from typing import Any, NoReturn, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."
UNREACH_MYPY_STUB = "UNREACH_MYPY_STUB"

P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, *, func_name: str, block_time: datetime):
        super().__init__(TOO_MUCH)
        self.func_name = func_name
        self.block_time = block_time


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ):
        errors = []
        if not isinstance(critical_count, int) or critical_count <= 0:
            errors.append(ValueError(INVALID_CRITICAL_COUNT))
        if not isinstance(time_to_recover, int) or time_to_recover <= 0:
            errors.append(ValueError(INVALID_RECOVERY_TIME))

        if errors:
            error_msg = VALIDATIONS_FAILED
            raise ExceptionGroup(error_msg, errors)

        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on
        self._state = "closed"
        self._failure_count = 0
        self._opened_at: datetime | None = None

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            self._check_open_state(func)
            try:
                result = func(*args, **kwargs)
            except self.triggers_on as exc:
                self._handle_exception(exc, func)
            else:
                self._reset()
                return result
            raise RuntimeError(UNREACH_MYPY_STUB)

        return wrapper

    def _check_open_state(self, func: CallableWithMeta[Any, Any]) -> None:
        if self._state != "open":
            return

        if self._opened_at is None:
            self._opened_at = datetime.now(UTC)

        time_since_opened = (datetime.now(UTC) - self._opened_at).total_seconds()
        if time_since_opened >= self.time_to_recover:
            self._state = "half-open"
        else:
            raise BreakerError(
                func_name=f"{func.__module__}.{func.__name__}",
                block_time=self._opened_at,
            )

    def _handle_exception(self, exc: Exception, func: CallableWithMeta[Any, Any]) -> NoReturn:
        if self._state == "half-open":
            self._open_circuit(func, exc)
        else:  # closed
            self._failure_count += 1
            if self._failure_count >= self.critical_count:
                self._open_circuit(func, exc)
            else:
                raise exc
        raise RuntimeError(UNREACH_MYPY_STUB)

    def _open_circuit(self, func: CallableWithMeta[Any, Any], cause: Exception | None = None) -> NoReturn:
        self._state = "open"
        self._opened_at = datetime.now(UTC)
        error = BreakerError(
            func_name=f"{func.__module__}.{func.__name__}",
            block_time=self._opened_at,
        )
        if cause is not None:
            raise error from cause
        raise error

    def _reset(self) -> None:
        self._state = "closed"
        self._failure_count = 0
        self._opened_at = None


circuit_breaker = CircuitBreaker(5, 30, Exception)


# @circuit_breaker
def get_comments(post_id: int) -> Any:
    """
    Получает комментарии к посту

    Args:
        post_id (int): Идентификатор поста

    Returns:
        list[dict[int | str]]: Список комментариев
    """
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
