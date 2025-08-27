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

# Query for top level scopes only, then print the number of items found
# as well as the module name and full hierarchical path to each object
top_scopes = verisium_debug_server.scopes()
print("Found " + str(len(top_scopes)) + " top level scopes:")
print('\n'.join("\tModule: " + t.declaration.name +
                ", Path: " + t.full_path
                for t in top_scopes))

# Query for all scopes four levels down from the top, then print the number
# of items found as well as the module name and full hierarchical path to
# each object
top_scopes4 = verisium_debug_server.scopes(ct.depth <=4)
print("\nFound " + str(len(top_scopes4)) + " scopes within 4 levels from top :")
print('\n'.join("\tModule: " + t.declaration.name +
                ", Path: " + t.full_path
                for t in top_scopes4))

# Query for a specific scopes matching a specific hierarchical path in the design
receiver_fifo = verisium_debug_server.scopes(ct.full_path == "uart_ctrl_top.uart_dut.regs.receiver.fifo_rx")[0]

# Print the Module, full_path, Declared file and Declared line as well as the type to the screen
print("\nPrinting specific scope (" + receiver_fifo.path + ") info: \n" +
      "\tModule: " + receiver_fifo.declaration.name + "\n" +
      "\tFull hierarchical path: " + receiver_fifo.full_path + "\n" +
      "\tDeclaration file: " + receiver_fifo.source.file + "\n" +
      "\tDeclaration line: " + str(receiver_fifo.source.line_start) + "\n" +
      "\tType: " + str(receiver_fifo.type))

# Close the verisium debug server
verisium_debug_server.close()


