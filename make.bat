@echo off

echo GENERATING CERTIFICATE...
mkdir build
"./bin/openssl.exe" req -x509 -newkey rsa:4096 -keyout build/key.pem -out build/cert.pem -days 24855 -nodes -config bin/openssl.cnf

echo COMPLILING CLIENT...
python -OO -m PyInstaller src/client.py --specpath build/  --onefile --add-data cert.pem;. --clean -y

echo COMPILING CONTROLLER...
python -OO -m PyInstaller src/controller.py --specpath build/ --onefile --add-data cert.pem;. --add-data key.pem;. --clean -y

echo DONE. EXECUTABLES IN DIST/