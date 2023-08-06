# TSR on Command Line

Browse thestudentroom.co.uk from the command line. Almost as lightweight as a real browser, and as strong and stable as the British government.

## Getting Started

### Prerequisites

#### Core

```
Python 3.5 or higher
tkinter (not pre-installed for Python 3 on some distros - sudo apt install python3-tk to install)
```

#### Optional

Python libraries:

```
psutil for displaying memory usage in non-POSIX operating systems
nltk and inflect for some basic word-crunching
subprocess to call a real browser
```

## Installation

```
pip install tsr
```

to use the PyPI repository version, or

```
pip install git+https://github.com/methmo/tsr
```

to use the latest version direct from this repository, replacing pip with pip3, depending on which version of python pip points to.

## License

MIT
