# Copyright 2023 Cadence Design Systems, Inc. All rights reserved worldwide.
#
# This source code ("Software") is part of the Verisium Debug API package, the proprietary
# and confidential information of Cadence or its licensors, and supplied
# subject to, and may be used only by Cadence's customer in accordance with a
# previously executed agreement between Cadence and that customer ("Customer").
#
# Permission is hereby granted to such Customer to use and make copies of this
# Software to connect and interact with a Cadence Verisium Debug product from
# Customer's Python program, subject to the following conditions:
#
# - Customer may not distribute, sell, or otherwise modify the Verisium Debug API package.
#
# - All copyright notices in this Software must be maintained on all included
#   Python libraries and packages used by Customer.

import argparse
import os

from verisium import *


# hello_verisium_debug.py
#
# This is a simple demo script that reads in user inputs for a path to a values database (SHM file)
# as well as a design database (Snapshot or LWD) and then launches Verisium Debug, prints out the server
# info for the running verisium debug as well as the top level scopes present in the debug db, then closes
# Verisium Debug.
# It can be used as a simple sanity test to ensure that Verisium Debugs's python API can connect to a design
#
# usage: hello_verisium_debug.py [-h] [-db INPUT_VALUES_DB_NAME]
#                        [-lwd INPUT_DESIGN_DB_NAME] [-nolwd NO_DESIGN_DB]
#
# optional arguments:
#   -h, --help            show this help message and exit
#   -db INPUT_VALUES_DB_NAME
#                         Path to a recorded simulation database (SHM file)
#   -lwd INPUT_DESIGN_DB_NAME
#                         Path to an elaborated design directory (xcelium.d dir)
#   -nolwd NO_DESIGN_DB   Set to True if you do not have a design directory

def print_pass():
    print("\t ____   __   ____  ____  ____  ____ ")
    print("\t(  _ \ / _\ / ___)/ ___)(  __)(    \\")
    print("\t ) __//    \\\\___ \\\\___ \ ) _)  ) D (")
    print("\t(__)  \_/\_/(____/(____/(____)(____/")
    print("\n\tSTATUS: PASSED.  Looks like the Verisium Debug Python API can read this design!")


def print_fail():
    print("\t (              (    (         (  ")
    print("\t )\ )    (      )\ ) )\ )      )\ )")
    print("\t(()/(    )\    (()/((()/(  (  (()/( ")
    print("\t /(_))((((_)(   /(_))/(_)) )\  /(_)) ")
    print("\t(_))_| )\ _ )\ (_)) (_))  ((_)(_))_  ")
    print("\t| |_   (_)_\(_)|_ _|| |   | __||   \  ")
    print("\t| __|   / _ \   | | | |__ | _| | |) | ")
    print("\t|_|    /_/ \_\ |___||____||___||___/ ")
    print("\n\tSTATUS: FAILED. Looks like the Verisium Debug Python API cannot read this design")


# If the user passes in arguments, great, store them to be used and no need to prompt the user
# for values later
parser = argparse.ArgumentParser()
parser.add_argument("-db", dest="input_values_db_name", default=None, help="Path to a recorded simulation database (SHM file)")
parser.add_argument("-lwd", dest="input_design_db_name", default=None, help="Path to an elaborated design directory (xcelium.d dir)")
parser.add_argument("-nolwd", dest="no_design_db", default=False, help="Set to True if you do not have a design directory")
args = parser.parse_args()
input_values_db_name = args.input_values_db_name
input_design_db_name = args.input_design_db_name
no_design_db = args.no_design_db

# If the user does not launch this script with switches, prompt the user for the
# needed information
#try:
verisium_debug_args = VerisiumDebugArgs()
if input_values_db_name is None:
    values_db_present = input("\nDo you want to connect to a values database (waveform SHM file)? (Y/N): ")
    values_db_present = values_db_present.strip()
    if values_db_present in ('y','Y'):
        input_values_db_name = input("\nPlease enter the path to a recorded simulation database (ex: /hm/user/design/ida.db/ida.shm): ")
        input_values_db_name = input_values_db_name.strip()
    else:
        input_values_db_name = None

if no_design_db == False:
    if input_design_db_name is None:
        design_db_present =  input("\nDo you want to connect to a design database (Elaborated Snapshot or LWD)? (Y/N): ")
        design_db_present = design_db_present.strip()
        if design_db_present in ('y','Y'):
            input_design_db_name = input("\nPlease enter the path to an elaborated design directory (ex: /hm/user/design/xcelium.d): ")
            input_design_db_name = input_design_db_name.strip()
        else:
            input_design_db_name = None

#Check to ensure we have at least one of either the LWD or the SHM file
if (input_values_db_name is None) and (input_design_db_name is None):
    print("\nERROR: You must provide either a values database or a design database to connect to. Please try again")
    print_fail()
    exit(1)

# Set the design database to use
if (input_design_db_name is None):
    verisium_debug_args.extra_args = "-nolwd "
else:
    if not os.access(input_design_db_name, os.R_OK):
        print("\nERROR: Can't find the design database (e.g. xcelium.d dir): " + input_design_db_name
              + ", Please check to ensure this path is valid and the directory exists.")
        print_fail()
        exit(1)
    # If the file exists, set the variable
    verisium_debug_args.extra_args = "-lwd " + input_design_db_name

# Set the values database to use
if (input_values_db_name is not None):
    # simple check you typed in a good path for the values DB
    if not os.access(input_values_db_name, os.R_OK):
        print("\nERROR: Can't find the values database (e.g. SHM file): " + input_values_db_name
              + ", Please check to ensure this path is valid and the file exists.")
        print_fail()
        exit(1)
    # If the file exists, set the variable
    verisium_debug_args.db = input_values_db_name

try:
    # launch Verisium Debug and establish a connection to it. This connection is represented by the VerisiumDebugServer
    # object instance verisium_debug_server.
    try:
        verisium_debug_server = verisiumdebugserver.VerisiumDebugServer(verisium_debug_args)
    except Exception as e:
        print("\nError while launching Verisum Debug: " + str(e))
        print("\nERROR: Failed to launch a Verisium Debug with the following arguments (please check the "
              "database format and try again):" + str(verisium_debug_args))
        print_fail()
        exit(1)
    else:
        print("\nVerisium Debug Successfully Launched. Here is a print of the ServerInfo object: \n"
              + str(verisium_debug_server.server_info))

    # get all the top-level scopes of the design
    top_level_scopes = verisium_debug_server.scopes()

    if len(top_level_scopes) > 0:
        print("\nFound " + str(len(top_level_scopes)) + " Top level scopes: \n"
              + "\n".join("\t"+t.full_path for t in top_level_scopes))

        # For each top level scope, print the signals
        for t in top_level_scopes:
            signals = t.signals()
            print("\nSignals of top level scope "+t.full_path+": \n")
            print("\n".join("\t"+s.full_path for s in signals))
    else:
        print("\nWARNING: No top level scopes found for design with: ")
        print("\t SHM File        : "+verisium_debug_args.db)
        print("\t Design Directory: "+input_design_db_name)

    # If we get to this point, we are successful
    print_pass()

finally:
    # If the server is actually launched, but something fatal happens during querying, close the server
    if 'verisium_debug_server' in vars():
        # close the Verisium Debug server and exit.
        verisium_debug_server.close()
    exit(0)
