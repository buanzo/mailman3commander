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

2. Install the dependencies and the package in editable mode:

   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

3. Invoke the console script:

   ```bash
   m3c
   ```

## Libraries in use
https://pypi.org/project/simple-term-menu/
https://pypi.org/project/mailmanclient/

## Libraries I would like to use:
https://pypi.org/project/easy-ansi/
https://pypi.org/project/blessed/
https://github.com/bchao1/bullet
