# netKeylog

LAN based keylogger with auto client detection

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

A windows machine with python 3 installed and the appropriate python packages, easily installable by executing 

```
pip install -r requirements.txt
```

## Deployment

To generate a controller / client pair run

```
python generator.py -o <output_dir>
```

## Documentation

Documentation available at <http://dekel1.reches.gitlab.io/netKeylog/>

## Built With

* [pyHook](https://sourceforge.net/projects/pyhook/) - The keyboard hook framework used
* [pywin32](https://sourceforge.net/projects/pywin32/) - Usage of several winAPI functions
* [PyCryptodome](https://github.com/Legrandin/pycryptodome/) - Used for encryption assurance

## Author

* **Dekel Reches** - *Everything* - [dekel1.reches](https://gitlab.com/dekel1.reches)

## Acknowledgments

* Me