# tidy-notes

> Keep plain-text notes organised from the terminal

tidy-notes sorts and indexes a folder of Markdown notes without any cloud service.

## Table of contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [License](#license)

## Features

- Index notes by tag
- Search by keyword
- Works fully offline

## Requirements

- Python 3.10+

## Installation

```bash
pip install tidy-notes
```

## Usage

```bash
tidy-notes index ~/notes
tidy-notes search budget
```

## Examples

**Find notes tagged #todo**

```bash
tidy-notes search --tag todo
```

## License

Distributed under the MIT License. Copyright (c) 2026 Example Org. See `LICENSE` for details.
