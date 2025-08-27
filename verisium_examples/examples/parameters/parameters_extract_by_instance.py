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

# Query the server for the top level design, looking down one level for
# an exact match on the instantiated name
design_top_list = verisium_debug_server.scopes(ct.name == "uart_dut", ct.depth <= 1)

# Store DUT in new variable
design_top = design_top_list[0]

# Query for all parameters in the design
parameters = design_top.signals(ct.declaration_type == DeclarationType.PARAMETER, ct.depth <= 99)

# Build a list of parent scopes, then reduce to a set to identify all scopes with
# parameters. The "path" field of a parameter contains the path to the enclosing scope
scope_list = [p.path for p in parameters]

# Convert to a set to remove duplicates in the list
scope_set = set(scope_list)

# Print the list of parameters again, but organized by scope
print("\nPrinting parameters based on scopes: \n")
for s in scope_set:
    # The scope_set list is a list of strings only.  In order to query for signals
    # We need to get the scope that contains the parameters
    scope = verisium_debug_server.scopes(ct.full_path == s)[0]

    # Query for parameters of the scope and bring them to the screen, with values
    scope_parameters = scope.signals(ct.declaration_type == DeclarationType.PARAMETER)
    print(str(len(scope_parameters)) + " parameters found within scope: " + str(scope.full_path))
    print('\n'.join("\t" + str(index) + ": " + str(sp.full_path) + ", Value: " +
                str(sp.value_at_time(ct.start_time == TimePoint('0ns'))) for index,sp in enumerate(scope_parameters)))

# Close the verisium debug server
verisium_debug_server.close()
