# Project Carvao

## Setput pptk
Make sure to install pptk dependencies:
```bash
# Go into pptk build folder
cd pptk/build/
# Install pptk dependencies
bash dependencies.sh
```
Update the following CMakeLists.txt variables on pptk root folder according to your build paths:
```bash
Numpy_INCLUDE_DIR
PYTHON_INCLUDE_DIR
Eigen_INCLUDE_DIR
TBB_INCLUDE_DIR
TBB_tbb_RUNTIME
TBB_tbbmalloc_LIBRARY
TBB_tbbmalloc_RUNTIME
```

Build the project and install the python wheel file:
```bash
bash run.sh
```

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
chmod +x extconverter
# Install qt dependencies
sudo apt install libtbb-dev patchelf libeigen3-dev qt5-default libpcl-io1.10
# Install pcl dependency
sudo apt install libpcl-io.10
```

## Running the script on Ubuntu (general case)
Just run the script as an executable:
```bash
# Execute script. Equivalent to: $ python3 pcselector.py
python3 pcselector.py
```
## Running the script on Ubuntu 18.04
Need to fix a pptk library issue with 18.04:
```bash
# Fix libz.so.1 library:
cd .env/lib/python3.6/site-packages/pptk/libs/
mv libz.so.1 libz.so.1.old
sudo ln -s /lib/x86_64-linux-gnu/libz.so.1
# Then run python main script in terminal. Equivalent to: $ python3 pcselector.py
python3 pcselector.py
```
