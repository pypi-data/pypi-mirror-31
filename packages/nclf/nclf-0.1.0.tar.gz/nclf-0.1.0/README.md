# nclf-python

nclf-python is an implementation of the
[New Command Line Format](https://github.com/peterkuma/nclf) (NCLF)
in python.

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

`nclf` is a command line program which decodes its NCLF command line arguments
and prints them as JSON to standard output.

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

### 0.1.0 (2018-05-02)

- Initial release (beta).
