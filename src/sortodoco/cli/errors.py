from enum import IntEnum

class ExitCode(IntEnum):
    OK = 0
    USAGE = 2
    NOT_FOUND = 3
    CONFIG = 4
    RUNTIME = 10

class CliError(Exception):
    exit_code: ExitCode = ExitCode.RUNTIME

class NotFoundError(CliError):
    exit_code = ExitCode.NOT_FOUND

class ConfigError(CliError):
    exit_code = ExitCode.CONFIG
