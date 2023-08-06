# Shared Context

Simplify the process of adding shared tests for python code.

## Usage

### `@behaves_like`

This is a class-level annotation that adds tests to the
unittest.TestCase subclass. It takes as input a list of functions that
each take the `self` argument. These functions will automatically have
`test_` prepended to them, so you don't have to do that.

You can also optionally specify kwargs to be passed in to all functions
(as kwargs).

See the [tests](tests/test_behaves_like.py) for examples of using this.

