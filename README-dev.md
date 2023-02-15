# Develper Guide for Maximo Visual Inspection (MVI) Validator



[MVI Validator](https://github.ibm.com/sustainability-software-japan/mvi-validator) is an accuracy validator for Maximo Visual Inspection.



## Getting Started



### Prerequisites

```sh
$ pip3 install --upgrade pip wheel
```



### Installing

```sh
$ git clone git@github.com:MountainField/dw.git
$ cd mvi-validator
$ pip3 install -e '.[dev]'
```



## Running Tests

The test code is written in [RSpec](https://rspec.info) style using [USpec](https://github.com/MountainField/uspec) and [PyHamcrest](https://github.com/hamcrest/PyHamcrest). But to run the tests you just execute `unittest`  that is built in test framework

```sh
$ python3 -m unittest discover -v -s src/tests -p '*_spec.py'
```



## Formatting Code

```sh
$ yapf --style='{column_limit: 9999}' -r  -i src 
```



## Build

```sh
$ rm -rf dist && python3 -m build
```



## Contributing

Open Issue [here](https://github.ibm.com/sustainability-software-japan/mvi-validator/issues) .



## Authors



Takahide Nogayama

<a href="https://github.ibm.com/NOGAYAMA"><img src="https://avatars.github.ibm.com/u/17184?s=460" width="100"/></a>



## License（ライセンス）

IBM Proprietary

