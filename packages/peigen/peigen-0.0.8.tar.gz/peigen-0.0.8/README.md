# peigen
Python wrapper for Eigen C++ headers

To use, include the following in your `setup.py` file:

```python
from peigen import header_path
```

then add `header_path` to the `include_dirs` list for any `Extension` modules that require Eigen.