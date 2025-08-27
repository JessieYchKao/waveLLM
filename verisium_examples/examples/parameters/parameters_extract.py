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

# Print the hierarchical path to all parameters and their values at time 0
print("Found " + str(len(parameters)) + " parameters within the design:")
print('\n'.join("\t" + str(index) + ": " + str(p.full_path) + ", Value: " +
                str(p.value_at_time(ct.start_time == TimePoint('0ns'))) for index,p in enumerate(parameters)))

# Close the verisium_debug server
verisium_debug_server.close()
