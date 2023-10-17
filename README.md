# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/iacopy/RCSB-Sync/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name             |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|----------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| src/download.py  |       94 |        0 |       30 |        0 |    100% |           |
| src/pdbparser.py |       58 |        1 |       34 |        4 |     95% |172->177, 188->194, 207, 219->216 |
| src/project.py   |      169 |        7 |       69 |        2 |     95% |   258-269 |
| src/rcsbids.py   |       22 |        0 |        8 |        0 |    100% |           |
| src/rcsbquery.py |       77 |        0 |       26 |        0 |    100% |           |
| src/utils.py     |       16 |        0 |        8 |        0 |    100% |           |
|        **TOTAL** |  **436** |    **8** |  **175** |    **6** | **97%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/iacopy/RCSB-Sync/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/iacopy/RCSB-Sync/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/iacopy/RCSB-Sync/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/iacopy/RCSB-Sync/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fiacopy%2FRCSB-Sync%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/iacopy/RCSB-Sync/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.