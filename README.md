Command-line Wrangler (CW)
============

[cw](https://github.com/MountainField/cw) is a data wrangling tool for command-line interface user.

- Example

    ```bash
    $ cat abc.csv | csv2markdown
    | a    | b    | c    |
    | ---- | ---- | ---- |
    | 1    | 1    | 1    |
    | 1    | 2    | 2    |
    | 2    | 1    | 3    |
    | 2    | 2    | 4    |
    
    $ cat abc.csv | cw-csv-pivot --field a --formula "sumc_c=sum(c)"
    | a    | sum_c |
    | ---- | ----- |
    | 1    | 3     |
    | 2    | 7     |
    ```


Installation
-----------

```bash
pip install cw
```

Contributing
------------

1. Clone this repo (`git clone git@github.ibm.com:data-science-at-command-line/cw.git`)
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -s -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create a new Pull Request


Author
-------

- **Takahide Nogayama** - [NOGAYAMA](https://github.ibm.com/NOGAYAMA)
