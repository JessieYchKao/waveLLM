#!/bin/bash
#/*-----------------------------------------------------------------
#File name     : env_setup.sh
#Developers    : Andrew Ding
#Created       : 02/2024
#Description   : Setup the enviroment for WAVE_LLM_ENV
#
#-------------------------------------------------------------------
#Copyright Andrew Ding 2024
#-----------------------------------------------------------------*/

# Biaseda Enviroment Setup 

# source /home/techdata/envScript/PrjSetup

# Project level Enviroment Setup 

export PRJ_HOME=`git rev-parse --show-toplevel`

# Set Yosys Path
export PATH=~/oss-cad-suite/bin:$PATH
export PATH=~/synlig:$PATH


# Create the python venv
# Name of the virtual environment directory
VENV_DIR="WAVE_LLM_ENV"
# Check if the virtual environment directory exists
if [ -d "$PRJ_HOME/$VENV_DIR" ]; then
    # The directory exists, which means the virtual environment is likely set up
    echo "A virtual environment already exists."

    echo "source $PRJ_HOME/$VENV_DIR/bin/activate"
    source $PRJ_HOME/$VENV_DIR/bin/activate

else
    # The directory does not exist, so we need to create a new virtual environment
    echo "Creating a new virtual environment..."
    
    # Check if Python 3 is installed and available
    if command -v python3.12 &>/dev/null; then
        # Create a new virtual environment using Python 3
        python3.12 -m venv "$VENV_DIR"
        source $PRJ_HOME/$VENV_DIR/bin/activate
        
        echo "Virtual environment created."
    else
        echo "Python 3.12 is not installed. Please install Python 3.12 to continue."
        exit 1
    fi
    pip3.12 install --upgrade pip
fi

if [ -f "./requirements.txt" ]; then
    pip3.12 install -r ./requirements.txt
else
    echo "No requirements.txt found execute from $PRJ_HOME to re-install dependencies"
fi


if [ -f "./cvdp_benchmark/requirements.txt" ]; then
    pip3.12 install -r cvdp_benchmark/requirements.txt
else
    echo "No cvdp_benchmark requirements.txt found execute from $PRJ_HOME to re-install dependencies"
fi


echo "WAVE_LLM_ENV ENVIROMENT ACTIVATED"



# Set environment variables to point to your custom OpenSSL
# !!! IMPORTANT: Use lib or lib64 based on your check above !!!
# export LDFLAGS="-L/usr/local/ssl/lib64"
# export LD_LIBRARY_PATH="/usr/local/ssl/lib64"
# export LD_LIBRARY_PATH=/usr/src/openssl-3.0.13/:$LD_LIBRARY_PATH
# export CPPFLAGS="-I/usr/local/ssl/include"


