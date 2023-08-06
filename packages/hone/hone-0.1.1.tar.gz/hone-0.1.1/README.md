# :knife: hone
Convert CSV to automatically nested JSON.

## Table of Contents
<!--ts-->
   + [Installation](#installation)
   + [Getting Started](#getting-started)
      + [Installation](#installation)
      + [Usage: Command Line](#usage-command-line)
      + [Usage: Python Module](#usage-python-module)
      + [Additional Configuration](#additional-configuration)
   + [Examples](#examples)
   + [License](#license)
<!--te-->

## Getting Started
Available as both a [Python module](#usage-python-module) and a [command line tool](#usage-command-line).

### Installation
```
pip install hone
```

### Usage: Command Line
To convert a CSV file located at `path/to/input.csv` to JSON (written to new file at `path/to/output.json`):

```
hone "path/to/input.csv" "path/to/output.json"
```

### Usage: Python Module
```
import hone

Hone = hone.Hone()
schema = Hone.get_schema('path/to/input.csv')   # returns nested JSON schema for input.csv
result = Hone.convert('path/to/input.csv')      # returns converted JSON as Python dictionary
```
### Additional Configuration
You can change the delimited characters that are used to generate the nested structure. By default, these are commas, underscores, and spaces. To change this, modify the [configuration file](hone/config.json).

## Examples

You can view all examples of conversions in the [examples](/examples) directory.
### CSV
| name  | birth day | birth month | birth year | reference | reference name | 
|-------|-----------|-------------|------------|-----------|----------------| 
| Bob   | 7         | May         | 1985       | TRUE      | Smith          | 
| Julia | 21        | January     | 1997       | FALSE     | N/A            | 
| Rick  | 12        | June        | 1996       | TRUE      | Clara          | 
### Generated JSON
```
[
  {
    "birth": {
      "day": "12",
      "month": "June",
      "year": "1996"
    },
    "name": "Rick",
    "reference": "TRUE",
    "reference name": "Clara"
  },
  {
    "birth": {
      "day": "12",
      "month": "June",
      "year": "1996"
    },
    "name": "Rick",
    "reference": "TRUE",
    "reference name": "Clara"
  },
  {
    "birth": {
      "day": "12",
      "month": "June",
      "year": "1996"
    },
    "name": "Rick",
    "reference": "TRUE",
    "reference name": "Clara"
  }
]
```
# License
Hone is licensed under the [MIT license](LICENSE).
