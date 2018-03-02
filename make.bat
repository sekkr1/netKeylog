@echo off

echo GENERATING CERTIFICATE...
mkdir build
"./bin/openssl.exe" req -x509 -newkey rsa:4096 -keyout build/key.pem -out build/cert.pem -days 24855 -nodes -config bin/openssl.cnf

echo COMPLILING CLIENT...
python -OO PyInstaller src/client.py --specpath build/  --onefile --add-data build/cert.pem;. --noconsole --clean

echo COMPILING CONTROLLER...
python -OO PyInstaller src/controller.py --specpath build/ --onefile --add-data build/cert.pem;. --add-data build/key.pem;. --noconsole --clean

echo DONE. EXECUTABLES IN DIST/