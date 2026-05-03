from __future__ import annotations


class AppError(Exception):
    '''Base application error for shared bot failures.'''


class InvalidCommandInputError(AppError):
    '''Raised when a command is missing required input or has invalid input.'''


class UpstreamDataError(AppError):
    '''Raised when an upstream data source fails or returns unusable data.'''
