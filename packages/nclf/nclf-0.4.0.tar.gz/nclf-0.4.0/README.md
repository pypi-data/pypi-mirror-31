# nclf-python

**Development status:** proposal

nclf-python is an implementation of the
[New Command Line Format](https://github.com/peterkuma/nclf) (NCLF)
in python.

Currently this implementation is Python 2 only.

## Example

```python
import sys
from nclf import nclf

args = nclf(sys.argv[1:])
print(args)
```

## Python API

### nclf

```python
nclf(args)
````

Arguments:

- `args` - command line arguments such as `sys.argv[1:]`

Decode NCLF arguments and return array of two elements representing NCLF
(see NCLF specification for details).

## Command line API

### nclf

```sh
nclf [arg...]
```

`nclf` is a command line program which decodes its NCLF command line arguments
and prints them as JSON to standard output.

### as_s

```sh
as_s [arg...]
```

as_s is a command line program which prints its arguments to standard output
as JSON strings separated by space. The only non-alphanumeric characters in the
output are `"`, ` ` and `\`.

## Install

- Install with pip:
    ```sh
    pip install nclf
    ```
- or use the file `nclf.py` directly in your program,
- or use the code in `nclf.py` directly in your program.

## License

[Public domain](LICENSE.md).

## Release notes

### 0.4.0 (2018-05-03)

- Add boolean named arguments.

### 0.3.0 (2018-05-03)

- Add literal strings following `=`.
- Add support for binary string values.

### 0.2.0 (2018-05-02)

- Add as_s.
- Change decoding of string arguments.

### 0.1.0 (2018-05-02)

- Initial release (beta).
