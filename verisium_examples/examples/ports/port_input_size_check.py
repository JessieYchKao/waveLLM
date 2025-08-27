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

# Query for scopes matching a specific hierarchical path in the design, to a max
# level two down from the top level
reg_list = verisium_debug_server.scopes(ct.full_path == "uart_ctrl_top.uart_dut.regs", ct.depth <= 2)

# Store the reg block in a new variable
reg = reg_list[0]

# Query for all ports in the reg block
reg_ports = reg.ports()

# Filter for input ports, then print all of the high connections and low connections
inputs = [p for p in reg_ports if p.direction == Direction.INPUT]

print("\nPorts for instance: " + str(reg.full_path))

# For each input port in the list, print all of it's connections
for i in inputs:
    print("\nPort connections for input port " + str(i.name) + ", size: " + str(i.size) + ":")
    # Print select fields of each high connection signal
    print('\n'.join("\t high_connection " + str(index) + ": \t" + str(conn.full_path) + ", " + str(conn.type) + ", " + str(conn.size)
                    for index,conn in enumerate(i.high_connections)))

    # Check that the sizes of the Port and the high connection match
    # By summing the bits, it also catches concatenations of bits into
    # bus within the port list
    bits = sum(hc.size for hc in i.high_connections)
    assert bits == i.size, "WARNING: High connection size mismatch!"

    # Print select fields of each low connection signal
    print("\t low_connection: \t\t" + str(i.low_connection.full_path) + ", " + str(i.low_connection.type) + ", " + str(i.low_connection.size))

    # Check that the size of the Port and the low connection match
    assert i.low_connection.size == i.size, "WARNING: Low connection size mismatch!"

# Close the verisium debug server
verisium_debug_server.close()
