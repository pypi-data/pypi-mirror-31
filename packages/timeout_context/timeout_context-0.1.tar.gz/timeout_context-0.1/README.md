# timeout_context
I created this python context because many problems I'm working with have the same problem: running a piece of code until it finishes. Hence, I found that the most pythonic way of doing that is to start a timeout context that raises an exception if the piece of code has not finished executing in the specified time.


## Instalation

     pip install timeout_context

## Usage

    >>> from timeout_context import Timeout, TimeoutException
    >>> def foo():
    ...     print "test"
    ...
    >>> with Timeout(3):
    ...     foo()
    ...
    test

If foo() take more than 3 seconds, the

## Tests

In the root folder of the project