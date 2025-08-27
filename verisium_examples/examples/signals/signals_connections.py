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
verisium_debug_args = VerisiumDebugArgs()

# Set the database to load when launching the Server
verisium_debug_args.db = "../APBUART_design/design/sim/SmartLogWaves.db"

# Launch a new Verisium Debug Server
verisium_debug_server = VerisiumDebugServer(verisium_debug_args)

# Query for scopes matching a specific hierarchical path in the design
read_fifo_list = verisium_debug_server.scopes(ct.full_path == "uart_ctrl_top.uart_dut.regs.receiver.fifo_rx")

# Store the read fifo in a new variable
read_fifo = read_fifo_list[0]

# Query for all signals in the read fifo
read_fifo_signals = read_fifo.signals()

# For each signal in the read_fifo, print index, name, type,
# size, # transitions to the screen
print("\nSignals for instance: " + str(read_fifo.full_path))
print('\n'.join("\t" + str(index) + ": \t" + str(s.name) + ", " + str(s.type) + ", " + str(s.size) +
                ", #Transitions: " + str(s.transition_count) for index,s in enumerate(read_fifo_signals)))

# Query for any clock signals within this module using a regex pattern match
clock_signal_list = read_fifo.signals(ct.name.matches("^cl.*k$"))

# For each clock in the list, print all of it's connections
for c in clock_signal_list:
    print("\nConnections for clock signal: " + str(c.name) + ":")
    # Obtain a list of all connections to the signal
    connected_signals = c.connections()
    # Print select fields of each connected signal
    print('\n'.join("\t" + str(index) + ": \t" + str(conn.full_path) + ", " + str(conn.type) + ", " + str(conn.size) +
                ", #Transitions: " + str(conn.transition_count) for index,conn in enumerate(connected_signals)))

# Close the verisium_debug server
verisium_debug_server.close()

