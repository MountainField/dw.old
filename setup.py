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
        name="cw",
        version="1.0.0",
        description="Command-line Wrangler (cw)",
        author="Takahide Nogayama",
        author_email="nogayama@jp.ibm.com",
        url="https://github.ibm.com/data-science-at-command-line/cw",
        download_url="https://github.ibm.com/data-science-at-command-line/cw/releases",
        license="IBM",
        
        package_dir={
            '': 'src'
            },
        packages=[
            "cw",
            ],
        package_data={
            'cw': [
                'completion/cw-completion.bash',
                ],
            },
        scripts=[
            "scripts/cw-csv-pivot",
            ],
        test_suite="tests",
    )
