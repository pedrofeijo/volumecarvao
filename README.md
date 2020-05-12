# Project Carvao

## Set up project
Proceed with the instalation of a python virtual environment:
```bash
# Get into the project path
cd volumecarvao
# Make sure virtualenv is installed
pip3 install virtualenv
# Create a virtual environment
virtualenv -p python3 .env 
# Activate virtual environment
source .env/bin/activate
# Install requirements
pip install -r requirements.txt
# Make script executable
chmod +x pcselector.py
```
## Running the script on Ubuntu 16.04
Just run the script as an executable:
```bash
# Execute script. Equivalent to: $ python3 pcselector.py
./pcselector.py
```
## Running the script on Ubuntu 18.04
Need to fix a pptk library issue with 18.04:
```bash
# Fix libz.so.1 library:
cd .env/lib/python3.6/site-packages/pptk/libs/
mv libz.so.1 libz.so.1.old
sudo ln -s /lib/x86_64-linux-gnu/libz.so.1
# Then run python main script in terminal. Equivalent to: $ python3 pcselector.py
./pcselector.py
```
