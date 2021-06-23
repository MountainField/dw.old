# -*- coding: utf-8 -*-

# =================================================================
# Licensed Materials - Property of IBM
#
# (c) Copyright IBM Corp. 2019, 2019 All Rights Reserved
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
# =================================================================

from setuptools import setup

if __name__ == "__main__":
    
    setup(
        name="dw",
        version="1.0.0",
        description="Data Wrangler (dw)",
        author="Takahide Nogayama",
        author_email="nogayama@gmail.com",
        url="https://github.com/MountainField/dw",
        download_url="https://github.com/MountainField/dw/releases",
        license="IBM",
        
        package_dir={
            '': 'src'
            },
        packages=[
            "dw",
            ],
        scripts=[
            "scripts/dw",
            ],
        test_suite="tests",
    )
