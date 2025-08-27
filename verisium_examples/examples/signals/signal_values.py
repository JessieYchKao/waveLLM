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

# Import the entire Verisium Debug package
from verisium import *

# Instantiate a VerisiumDebugArgs class to pass in command line arguments
# to a Verisium Debug Server
verisium_debug = VerisiumDebugArgs()

# Set the database to load when launching the Server
verisium_debug.db = "../APBUART_design/design/sim/SmartLogWaves.db"

# Launch a new Verisium Debug Server
verisium_debug_server = VerisiumDebugServer(verisium_debug)

# Query for scopes matching a specific hierarchical path in the design
read_fifo_list = verisium_debug_server.scopes(ct.full_path == "uart_ctrl_top.uart_dut.regs.receiver.fifo_rx")

# Store the read fifo in a new variable
read_fifo = read_fifo_list[0]

# Query for all signals in the read fifo
read_fifo_signals = read_fifo.signals()

# Print all of the signals extracted from the scope, along with their values
for index,s in enumerate(read_fifo_signals):
    # Extract all values of the signal
    values = s.values()
    # Print the signal name, the number of transitions and then all values
    print("\n[" + str(index) + "]: " + s.full_path + ", Transitions: " + str(s.transition_count) + ":")
    for v in values:
        print("Time/Value: " + str(v.time.time) + "/" + v.value)

# Close the verisium debug server
verisium_debug_server.close()
