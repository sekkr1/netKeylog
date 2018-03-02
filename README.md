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

To generate a controller / client pair run on an elevated prompt

```
make
```

And the output executable will be under the folder dist/

## Paperwork

Project paperwork available at the [Wiki](https://gitlab.com/dekel1.reches/netKeylog/wikis/)

## Built With

* [keyboard](https://github.com/boppreh/keyboard/) - The keyboard hook framework used
* [pywin32](https://sourceforge.net/projects/pywin32/) - Usage of several winAPI functions
* [PyCryptodome](https://github.com/Legrandin/pycryptodome/) - Used for encryption assurance
* [TkInter](https://wiki.python.org/moin/TkInter/) - GUI framework used
* [PyInstaller](http://www.pyinstaller.org/) - Python executable compiler
* [OpenSSL](https://www.openssl.org/) - Private key - Certificate pair generation

## Author

* **Dekel Reches** - *Everything* - [dekel1.reches](https://gitlab.com/dekel1.reches)

## Acknowledgments

* Me