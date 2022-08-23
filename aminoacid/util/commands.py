from __future__ import annotations

from inspect import signature
from time import time
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    List,
    Literal,
    Optional,
    TypeVar,
    Union,
)

from ..exceptions import CheckFailed, CommandNotFound

if TYPE_CHECKING:
    from ..abc import Context

T = TypeVar("T")


class UserCommand:
    """Command defined by User"""

    def __init__(
        self,
        func: Callable[..., Coroutine[Any, Any, T]],
        command_name: str = "",
        check: Optional[Callable[[Context], bool]] = None,
        check_any: Optional[List[Callable[[Context], bool]]] = list(),
        cooldown: Optional[int] = 0,
    ) -> None:
        """Initialises a new UserCommand with a given function to call and a given name

        Parameters
        ----------
        func : Callable[..., Coroutine[Any, Any, T]]
            The function that is called when the command is executed
        command_name : str, optional
            Name of the command, by default the function name
        check : Optional[Callable[[Context], bool]], optional
            Function which is called to see if the command may be called, by default always True
        check_any : Optional[List[Callable[[Context], bool]]], optional
            List of checks, command will execute if any of them return True, by default []
        cooldown : Optional[int]
            Time to sleep before another instance of this command can be executed by the same user
        """

        self.callback = func
        self.check = check
        self.check_any = check_any
        self.cooldown = cooldown
        self.name = command_name or func.__name__

        self.calls = {}

    def get_signature(self) -> str:
        """Returns the signature of the Command

        Returns
        -------
        str
            Signature of the command
        """

        params = signature(self.callback).parameters
        result = list()
        for name, param in params.items():
            optional = bool(param.default)
            annotation: Any = param.annotation
            origin = getattr(annotation, "__origin__", None)
            if origin is Union:
                none_cls = type(None)
                union_args = annotation.__args__
                optional = union_args[-1] is none_cls
                if len(union_args) == 2 and optional:
                    annotation = union_args[0]
                    origin = getattr(annotation, "__origin__", None)
            if origin is Literal:
                name = "|".join(
                    f'"{v}"' if isinstance(v, str) else str(v)
                    for v in annotation.__args__
                )
            if optional:
                result.append(f"[{name}]")
            elif param.kind == param.VAR_POSITIONAL:
                result.append(f"[{name}...]")
            else:
                result.append(f"<{name}>")
        return " ".join(result)

    def __call__(
        self, context: Context, *args: Any, **kwargs: Any
    ) -> Coroutine[Any, Any, T]:
        """Allow the Command to be executed by calling the UserCommand instance.
        like `await UserCommand()`

        Parameters
        ----------
        context : Context
            Context to pass to the callback

        Returns
        -------
        T
            returns the Callback return value
        """

        if not any(
            check(context) for check in self.check_any or [lambda _: True]
        ) or not self.check(context):
            return context.client.logger.exception(CheckFailed(context))
        if (current_time := int(time())) <= self.calls.get(
            context.author.id, 0
        ) + self.cooldown:
            return
        self.calls[context.author.id] = current_time
        context.client.logger.warning((self.calls, self.cooldown))
        return self.callback(context, *args, **kwargs)

    def __str__(self) -> str:
        return self.get_signature()

    def __repr__(self) -> str:
        return str(self)


class HelpCommand(UserCommand):
    def __init__(self) -> None:
        super().__init__(self.help, "help")

    async def help(self, ctx: Context, command: str = ""):
        if not command:
            await ctx.send(
                f"\n".join(
                    [
                        ctx.client.prefix + name
                        for name, _ in ctx.client.__command_map__.items()
                    ]
                )
            )
        if command not in ctx.client.__command_map__:
            return ctx.client.logger.exception(CommandNotFound(ctx))
        await ctx.send(ctx.client.__command_map__[command].get_signature())
