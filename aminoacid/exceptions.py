from logging import getLogger

logger = getLogger(__name__)


class AminoBaseException(Exception):
    """Base Class for AminoAcid Exceptions, all exceptions use this as a base class"""

    ...


class UnknownExcepion(AminoBaseException):
    ...


class AccessDenied(AminoBaseException):
    ...


class UnsupportedService(AminoBaseException):
    ...


class InvalidRequest(AminoBaseException):
    ...


class InvalidSession(AminoBaseException):
    ...


class InvalidAccountOrPassword(AminoBaseException):
    ...


class InvalidDevice(AminoBaseException):
    ...


class TooManyRequests(AminoBaseException):
    ...


class ActionNotAllowed(AminoBaseException):
    ...


def handle_exception(code: int, data=None):
    """Puts an Exception with the given error code into the logger with Exception severity

    Parameters
    ----------
    code : int
        The api:statuscode
    """
    # TODO: Complete this list
    logger.exception(
        {
            106: AccessDenied,
            103: InvalidRequest,
            104: InvalidRequest,
            105: InvalidSession,
            100: UnsupportedService,
            110: ActionNotAllowed,
            200: InvalidAccountOrPassword,
            218: InvalidDevice,
            219: TooManyRequests,
        }.get(code, UnknownExcepion)(data)
    )


class CommandNotFound(AminoBaseException):
    ...


class CommandExists(AminoBaseException):
    ...


class CheckFailed(AminoBaseException):
    ...
