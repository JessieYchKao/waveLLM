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

# Import the entire Verisium package
from verisium import *

# Import the sys package to access the sys.maxsize number
# which can be used to represent the largest number possible
# on the machine.  This is used in setting the hierarchical
# depth for queries
import sys

# Instantiate a VerisiumDebugArgs class to pass in command line arguments
# to a VerisiumDebug Server
verisium_debug_args = VerisiumDebugArgs()

# Set the database to load when launching the Server
verisium_debug_args.db = "../APBUART_design/design/sim/SmartLogWaves.db"

# Launch a new Verisium Debug Server
verisium_debug_server = VerisiumDebugServer(verisium_debug_args)

# Query for the dut harness using an exact match on the full path to the DUT from
# the top level of the hierarchy.  Return the list item.
dut_harness = verisium_debug_server.scopes(ct.full_path == "uart_ctrl_top")[0]

# Query for all instances of a the raminfr module within 10 levels of the dut_harness
# then print their Module name and hierarchical path
rams = dut_harness.scopes(ct.declaration_name == "raminfr", ct.depth <=10)
print("\nFound " + str(len(rams)) + " instances of the raminfr module within 10 levels down from "
      + dut_harness.full_path + ":")
print('\n'.join("\t["+str(index)+"]: Module: " + r.declaration.name + ", Path: " + r.full_path
                for index,r in enumerate(rams)))

# Query for all scopes whose module name ends with "_if" in the design and
# then print the module name and the full path to the screen
interface_scopes = dut_harness.scopes(ct.depth <= 10, ct.declaration_name.matches('.*_if$'))
print("\nFound " + str(len(interface_scopes)) + " interfaces within 10 levels from " + dut_harness.full_path + " :")
print('\n'.join("\t[" + str(index) + "]: Module: " + i.declaration.name +
                ", Path: " + i.full_path
                for index,i in enumerate(interface_scopes)))

# Query for all clocking blocks within the design.  In this design, the clocking blocks
# are all contained within PSL (assertion language) code.
clocking_blocks = dut_harness.scopes(ct.depth <= 10,
                                     ct.declaration_name.contains("clocking"),
                                     ct.path.contains("uart_dut"))

# Print the number of clocking blocks found, as well as the instance name, the module name,
# hierarchical path, declared file and line number
print("\nFound " + str(len(clocking_blocks)) + " clocking blocks within 10 levels from " +
      dut_harness.full_path + " with \"uart_dut\" in their path:")
print('\n'.join("\t["+str(index)+"]: \tName: " + c.name + "\n" +
                "\t\tModule: " + c.declaration.name + "\n" +
                "\t\tPath: " + c.full_path + "\n" +
                "\t\tDeclaration file: " + c.source.file + "\n" +
                "\t\tDeclaration line: " + str(c.source.line_start)
                for index,c in enumerate(clocking_blocks)))

# Search for any scope whose definition in the file is more than 50 lines deep in the file.
declared_late = verisium_debug_server.scopes(ct.depth <= sys.maxsize, ct.line > 50)
print("\nFound " + str(len(declared_late)) + " scopes whose declaration line is greater than 50")
print('\n'.join("\t["+str(index)+"]: \tModule: " + dl.declaration.name + "\n" +
                "\t\tFull hierarchical path: " + dl.full_path + "\n" +
                "\t\tDeclaration file: " + dl.source.file + "\n" +
                "\t\tDeclaration line: " + str(dl.source.line_start)
                for index,dl in enumerate(declared_late)))

# Close the verisium debug server
verisium_debug_server.close()
