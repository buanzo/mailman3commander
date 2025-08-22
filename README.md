# NOTE: Work in progress, no package uploaded to pypi yet

# Mailman3 Commander

m3c is a simple console tool which helps you manage your Mailman3 setup. The tool is self-explanatory—just run `m3c`.

## Installation

Once published to PyPI you will be able to install the package with:

```bash
pip install mailman3commander
```

### Local setup

Until then you can run the project from source:


1. Clone the repository and move into it:

   ```bash
   git clone https://github.com/buanzo/mailman3commander.git
   cd mailman3commander
   ```

2. Install the package in editable mode (this will install dependencies automatically):

   ```bash
   pip install -e .
   ```

3. Invoke the console script:

   ```bash
   m3c
   ```

### Build

To build a distribution package locally, install the build tool and run:

```bash
python -m pip install --upgrade build
python -m build
```

# Libraries in use

- [simple-term-menu](https://pypi.org/project/simple-term-menu/)
- [buanzobasics](https://pypi.org/project/buanzobasics/)
- [mailmanclient](https://pypi.org/project/mailmanclient/)


## Libraries I would like to use:
https://pypi.org/project/easy-ansi/
https://pypi.org/project/blessed/
https://github.com/bchao1/bullet
