# Data Wrangler (dw)

[dw](https://github.com/MountainField/dw) is a data wrangling tool for command-line interface user.

- Example

    ```bash
    $ cat abc.csv | dw csv to_markdown
    | a    | b    | c    |
    | ---- | ---- | ---- |
    | 1    | 1    | 1    |
    | 1    | 2    | 2    |
    | 2    | 1    | 3    |
    | 2    | 2    | 4    |
    
    $ cat abc.csv | dw csv pivot --field a --formula "sumc_c=sum(c)"
    | a    | sum_c |
    | ---- | ----- |
    | 1    | 3     |
    | 2    | 7     |
    ```


## Setup

```bash
pip install git+https://github.com/MountainField/dw
```

Author
------

- **Takahide Nogayama** - [Nogayama](https://github.com/nogayama)


License
-------

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details

Contributing
------------

Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

