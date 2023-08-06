# EXJSON 
## Extended JSON Parser for Python

*This Project is currently in Alpha State*

### Introduction
This project was born as part of a toolset I required for another project of mine. EXJSON is layer over the Python Standard JSON decoder library, which implements functionality not currently supported by it while trying to keep compliant with the JSON standard as much as possible.

### Supported Python Versions
- Python 3.x

### Install

```sh
pip install git+https://github.com/prods/exjson.git
```

### Sample

**samplefile1.json**
```json
{
  // Sample Property
  "name": "test file",
  // Sample value set with an included object
  "values": [
    /* INCLUDE "samplefile2.json" */
    {
      "value_id": "923ko30k3",
      "value": "Another Value"
    }
  ]
}
```

**samplefile2.json**
```json
/*
  INCLUDIBLE TEST FILE
*/
{
   "value_id": "93987272",
   "value": "This Value"
}
```

**Usage**
```python
import exjson as json

# Decode
sample_value_set = json.loads("./samplefile1.json")

# ... Do stuff with sample_value_set

# Encode
with open("./result.json") as f:
    f.write(json.dumps(sample_value_set))

```

**result.json**
```json
{
  "name": "test file",
  "values": [
    {
       "value_id": "93987272",
       "value": "This Value"
    },
    {
      "value_id": "923ko30k3",
      "value": "Another Value"
    }
  ]
}
```

For more complex examples please check the [unit tests](https://github.com/prods/exjson/tree/master/tests).


### API
The exjson API offers similar API to the one available on the Python standard JSON decoder/encoder library. 

* **loads**(json_file_path, encoding=None, cls=None, object_hook=None, parse_float=None,
          parse_int=None, parse_constant=None, object_pairs_hook=None, error_on_include_file_not_found=False, \*\*kw)
          
  **Arguments:**
  - `json_file_path`: main json file to be loaded.
  - `encoding`: encoding codec to use when loading the file and all included files. All included files should use the same encoding.
  - `cls`: if specified, it uses the provided custom JSONDecoder instance to decode the json file. [See Python docs for details.](https://docs.python.org/3/library/json.html#json.JSONDecoder)
  - `object_hook`: if specified, it will be called for every decoded JSON object and its value will be used instead of the default `dict`. [See Python docs for details.](https://docs.python.org/3/library/json.html#json.JSONDecoder)
  - `parse_float`: if specified, it will be called for every `float` that is decoded. [See Python docs for details.](https://docs.python.org/3/library/json.html#json.JSONDecoder)
  - `parse_int`: if specified, it will be called for every `int` that is decoded. [See Python docs for details.](https://docs.python.org/3/library/json.html#json.JSONDecoder)
  - `parse_constant`: if specified, will be called with one of the following strings: '-Infinity', 'Infinity', 'NaN'. [See Python docs for details.](https://docs.python.org/3/library/json.html#json.JSONDecoder)
  - `object_pairs_hook`: if specified, it will be called for every decoded JSON object with an ordered list of pairs. Its result will be used instead of the default `dict`. [See Python docs for details.](https://docs.python.org/3/library/json.html#json.JSONDecoder)
  - `error_on_included_file_not_found`: if set to `True` an Exception is raised if an included file is not found.
  
  **Supported Extended Functionality:**
   - Supports #INCLUDE directive. 
   - Supports single-line and multi-line C style comments
   
* **dumps(obj, skipkeys=False, ensure_ascii=True, check_circular=True,
          allow_nan=True, cls=None, indent=None, separators=None,
          default=None, sort_keys=False, \*\*kw)**
          
  **Arguments:**
  - `obj`: object instance to encode (serialize).
  - `skipkeys`: If set to `False` a `TypeError` is raised if the keys are not primitive types (`int`, `str`, `float` or `None`). [See Python docs for details.](https://docs.python.org/3/library/json.html#json.JSONEncoder)
  - `ensure_ascii`: If set to `True` all Incoming ASCII characters will be escaped in the output, else they will kept as-is. [See Python docs for details.](https://docs.python.org/3/library/json.html#json.JSONEncoder)
  - `check_circular`: If set to `True` will check all classes and dictionaries for prevent circular references in order to prevent infinite recursion. [See Python docs for details.](https://docs.python.org/3/library/json.html#json.JSONEncoder)
  - `allow_nan`: If set to `True`, `NaN`, `Infinity`, and `-Infinity` will be encoded as such. [See Python docs for details.](https://docs.python.org/3/library/json.html#json.JSONEncoder)
  - `cls`: [See Python docs for details.](https://docs.python.org/3/library/json.html#json.JSONEncoder)
  - `indent`: If set to `True` the output json will be indented. [See Python docs for details.](https://docs.python.org/3/library/json.html#json.JSONEncoder)
  - `separators`: If specified, it should be a tuple listing the item and key separators to use during encoding. [See Python docs for details.](https://docs.python.org/3/library/json.html#json.JSONEncoder)
  - `default`: [See Python docs for details.](https://docs.python.org/3/library/json.html#json.JSONEncoder.default)
  - `sort_keys`: It set to `True` the output dictionary will be sorted by key. [See Python docs for details.](https://docs.python.org/3/library/json.html#json.JSONEncoder)
          
  **Supported Extended Functionality:**
  - Does not support #INCLUDE directive.
  - Does not support comments.

### Extended Features:
 * C Style Include directive
 Loads specified file from the same path where the file is being loaded.
 Supports 2 syntax always enclosed in comments:
 ```c
/* #INCLUDE <_secondary.json> */

// #INCLUDE <_secondary.json>

/* #INCLUDE "_secondary.json" */

// #INCLUDE "_secondary.json"
```

* C Style Comments
Supports C Style Comments.
Single-Line
```c
// TEST

/* TEST */
```

```c
/* 
TEST
*/
```

### How does it work:

#### Deserialization
It uses CPython if available or the Standard Python JSON parser library if not available.

#### Includes
The `#INCLUDE <*>` directives are identified in the file and the file name enclosed in `< >` or `" "` is extracted. Then the XJson include logic looks for the file in the same path where the main json file is located. Once the file is found the file content is loaded and placed in the location where the `#INCLUDE` directive was located. If the file is not found the `#INCLUDE` directive is ignored and removed when all comments are dropped or an exception can be raised if the `error_on_include_file_not_found` argument is set to `True` when calling `loads()`. Another cool behavior of the include functionality is that it will automatically add a comma at the end of the `#INCLUDE` if it determines that the json file was included in a location where it is followed by more json content. This allows makes it simple to include files without worrying about where it should go.

**It is not recommended to included JSON files that are full and valid json. This make it easy to validate in isolation. Never #INCLUDE a partial json that cannot be validated by itself... but you can...** 

#### C Style Comments
Its simple. Comments are removed in memory before deserialization. This allows the Standard Python JSON parser deserialize the JSON file.

### Road Map:
* More unit tests
* Value Reference from same or different file. Accessible by JSON property tree.
* Basic Scripting. Dynamic values support. Example: Date Calculation and formatting.
* Support serialization to multiple files by using `__exjson_file__ = "filename.json"` property.
* Benchmarking?

