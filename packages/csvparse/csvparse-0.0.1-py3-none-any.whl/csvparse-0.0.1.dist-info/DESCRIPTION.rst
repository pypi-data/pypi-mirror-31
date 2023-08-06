# CSV Parse

CSV Parse is a simple state-machine based approach to parsing CSV files.  It's creation was motivated after dealing with some CSV parsers that could not properly handle strings with null bytes.  It is not very fast, and definitely not very memory efficient, but if you want to explore simple CSV parsing, look no further.  If you have CSV files that are incorrectly formatted, you can pretty easily modify the code to patch them up.

## Usage

CSV parse supports reading from files or a buffer.

### Reading Files

```python
from csv_parse import read

data = read("/home/user/foo.txt")
```

### Reading a buffer

```python
from csv_parse import parse

my_string = 'foo,bar\nbaz,bat'
size = len(my_string)
data = parse(my_string, size)
```

CSV Parse also supports escaping, custom delimiters and newlines, and custom quoting.

```python
data = read("/home/user/foo.txt", field_separator=',', null_as="", newline="\n", quote='"')
```


# Changelog

## 0.0.1

* Initial Release


