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

from verisium import *

# Import the json python package
import json

# Instantiate a VerisiumDebugArgs class to pass in command line arguments
# to a verisium debug Server
verisium_debug_args = VerisiumDebugArgs()

# Set the database to load when launching the Server
verisium_debug_args.db = "../APBUART_design/design/sim/SmartLogWaves.db"

# Launch a new Verisium Debug Server
verisium_debug_server = VerisiumDebugServer(verisium_debug_args)

# Query for the dut instance and return the list item (there should only be one)
dut = verisium_debug_server.scopes(ct.full_path == "uart_ctrl_top.uart_dut")[0]

# Extract all signals down to a certain depth
signals = verisium_debug_server.signals()

def write_signals(signals, filename="signals", format="text"):
    ''' This method will write signals to a file in a user-specified format.
    default format for the printed list is text
    '''
    if (format == "text"):
        wfile = filename + ".txt"
        ftext = open(wfile, "w+")
        # Iterate over the signal list, printing values
        for sindex,s in enumerate(signals):
            pstring = "[" + str(sindex) + "]: " + str(s.full_path) + ", Transitions: " + str(s.transition_count) + "\n"
            ftext.write(pstring)

            # Next, extract the signal values
            values = s.values()
            for vindex, v in enumerate(values):
                pstring = "\t[" + str(vindex) + "]: " + str(v.time.time) + " fs, " + v.value + "\n"
                ftext.write(pstring)
        # Close the text file we are writing to
        ftext.close()

    if (format == "json"):
        wfile = filename + ".json"
        signal_dict = {}
        # Iterate over the signal list, printing values
        for sindex, s in enumerate(signals):

            # Create a new dictionary entry for each signal
            signal_dict[s.full_path] = []

            # Next, extract the signal values
            values = s.values()
            for vindex, v in enumerate(values):
                # Append transitions to the signal dictionary entry
                signal_dict[s.full_path].append({
                    str(v.time.time): v.value
                })
        # Print the signals and values as a JSON file, with pretty-print
        # options to indet by 4 characters and sort the keys in ascending order
        # (which should be the case automatically)
        with open(wfile,"w+") as outfile:
            json.dump(signal_dict,outfile, indent=4, sort_keys=True)

        # Close the text file we are writing to
        outfile.close()

    if (format == "csv"):
        wfile = filename + ".csv"
        signal_dict = {}
        # Iterate over the signal list, extracting values
        for sindex, s in enumerate(signals):

            # Create a new dictionary entry for each signal
            signal_dict[s.full_path] = []

            # Next, extract the signal values
            values = s.values()
            for vindex, v in enumerate(values):
                # Append transitions to the signal dictionary entry
                signal_dict[s.full_path].append({
                    str(v.time.time): v.value
                })
        # Open a CSV file and write the values as
        # signal, Time, Value
        with open(wfile,"w+") as outfile:

            # Write the header of the CSV file
            outfile.write("Signal,Time (fs),Value\n")

            # Split the signal_dict dictionary by key/value pairs
            for skey,svalues in signal_dict.items():
                # The svalues returned value for the dictionary item
                # is actually a list of time/value dictionary items
                # so we iterate over those next
                for time_value_pair in svalues:

                    # Next, we split each list element (which is a dictionary
                    # into a key/value pair and write them to the csv file
                    for tkey,tvalue in time_value_pair.items():
                        # Here we write the signal name (skey), Time (tkey) and value (tvalue)
                        outfile.write(skey+"," + str(tkey) + "," + tvalue + "\n")
        # Close the text file we are writing to
        outfile.close()


# Write the signals and values to various text formats
# Simple text
write_signals(signals)
# JSON format
write_signals(signals,format="json")

# CSV format
write_signals(signals,format="csv")

# Print simple completion message to the screen for users
print("signals_write_to_text.py completed!  Check the local directory for signals.json, signals.csv and signals.txt files")

# Close the Verisium Debug server
verisium_debug_server.close()

