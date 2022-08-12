from __future__ import annotations

from inspect import signature
from typing import Any, Callable, TypeVar, Coroutine, TYPE_CHECKING

if TYPE_CHECKING:
    from ..abc import Context

T = TypeVar("T")


class UserCommand:
    def __init__(
        self, func: Callable[..., Coroutine[Any, Any, T]], command_name: str = ""
    ) -> None:
        """Initialises a new UserCommand with a given function to call and a given name

        Parameters
        ----------
        func : Callable[..., Coroutine[Any, Any, T]]
            The function that is called when the command is executed
        command_name : str, optional
            Name of the command, by default the function name
        """
        self.callback = func
        """This callback is the function to be executed whenever the command is called.
        """
        self.name = command_name or func.__name__

    def get_signature(self) -> str:
        """Returns the signature of the Command

        Returns
        -------
        str
            Signature of the command
        """
        return f"{self.name}{signature(self.callback)}"

    def __call__(self, *args: Any, **kwargs: Any) -> Coroutine[Any, Any, T]:
        return self.callback(*args, **kwargs)

    def __await__(self, context: Context, *args: Any, **kwargs: Any) -> T:
        """Allow the Command to be executed by calling the UserCommand instance.
        like ```
        await UserCommand()
        ```

        Parameters
        ----------
        context : Context
            Context to pass to the callback

        Returns
        -------
        T
            returns the Callback return value
        """
        return self.callback(context, *args, **kwargs).__await__()

    def __str__(self) -> str:
        return self.get_signature()

    def __repr__(self) -> str:
        return str(self)


class HelpCommand(UserCommand):
    def __init__(self) -> None:
        super().__init__(self.help, "help")

    async def help(self, ctx: Context):
        # TODO: Implement a basic help command
        await ctx.send("")
