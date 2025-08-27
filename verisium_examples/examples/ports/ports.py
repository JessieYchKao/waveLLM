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

print("\nPorts for instance: " + str(reg.full_path))

# For each port in the reg block, print index, name, direction, size, # transitions to the screen
print('\n'.join("\t" + str(index) + ": \t" + str(p.name) + ", " + str(p.direction) + ", " + str(p.size)
                for index, p in enumerate(reg_ports)))

# Close the verisium debug server
verisium_debug_server.close()
