# sequence2hash - Convert sequence to hash
This tool converts a valid value in a sequence to a hash and contains a path to a valid value in the key field

## Features
- Convert valid values in the sequence to hashes
- Paths showing valid values in the key field
- Valid values not (), [], {}, None, ''

## Requirements
- Does not require any third party libraries

## Installation
```Bash
pip install sequence2hash
```

## Examples
Define the sequence variable:
```Python
parameters = {
    'queryKey': '',
    'constraints': {
        'ids': [],
        'phids': (),
        'name': 'Operating platform'
        'members': ('Bunoob', 1944, 'Google'),
        'watchers': [],
        'status': '',
        'isMilestone': True,
        'icons': [],
        'colors': ['blue', '', 'red', ''],
        'parents': [],
        'ancestors': [],
    },
    'attachments': {
        'subscribers': None
    },
    'order': 'newest',
    'before': '',
    'after': '',
    'limit': {}
}
```
Transfer:
```Python
import sequence2hash
for x in sequence2hash.flatten(parameters):
    print(x)
```
Output:
```Bash
{'key': ['constraints', 'name'], 'value': 'Operating platform'}
{'key': ['constraints', 'members', '0'], 'value': 'Bunoob'}
{'key': ['constraints', 'members', '1'], 'value': 1944}
{'key': ['constraints', 'members', '2'], 'value': 'Google'}
{'key': ['constraints', 'isMilestone'], 'value': True}
{'key': ['constraints', 'colors', '0'], 'value': 'blue'}
{'key': ['constraints', 'colors', '2'], 'value': 'red'}
{'key': ['order'], 'value': 'newest'}
```

## Credits
- [Python Cookbook 3rd Edition Documentation](http://python3-cookbook.readthedocs.io/zh_CN/latest/) : Life is short and I use Python!
