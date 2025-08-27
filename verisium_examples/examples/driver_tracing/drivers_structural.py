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

# Import the entire VerisiumDebug package to access all datatypes needed
from verisium import *

# Instantiate a VerisiumDebugArgs class to pass in command line arguments
# to a Verisium Debug Server
verisium_debug_args = VerisiumDebugArgs()

# Set the database to load when launching the Server
verisium_debug_args.db = "../APBUART_design/design/sim/SmartLogWaves.db"

# Launch a new Verisium Debug Server
verisium_debug_server = VerisiumDebugServer(verisium_debug_args)

# Extract all signals in the design that have "bus" in the name
signals_to_trace = verisium_debug_server.signals(ct.name.contains("bus"), ct.depth >= 0)

# Print the signals to the screen that match the query
print('Signals that match \'bus\' in the design: \n'.join(str(index) + ": \t" + str(a.name) + ", " + str(a.full_path) +
         ", #Transitions: " + str(a.transition_count) for index,a in enumerate(signals_to_trace)))

# Specify an arbitrary time in the simulation as we will be querying
# for values of contributors at this time
verisium_debug_server.set_time(TimePoint("10000ns"))

# For each extracted signal, query the drivers and contributors
# and print them to the screen.
for s in signals_to_trace:
    print("\nDrivers for signal: " + s.full_path )
    drivers = s.drivers()
    for dindex,d in enumerate(drivers):
        print("\tDriver [" + str(dindex) + "]: \n"
              + "\t\tName: " + d.name
             )
        # Query for the contributors of the driver and print names and values to the screen
        driver_contributors = d.contributors()
        for cindex,c in enumerate(driver_contributors):
              print("\t\tContributor [" + str(cindex) + "]: \n"
              + "\t\t\tfull_path: " + c.full_path + "\n"
              + "\t\t\tvalue: " + c.value_at_time(ct.start_time == verisium_debug_server.time()) + "(@time: " + verisium_debug_server.time().label + ")"
              )

# Close out the Verisium Debug Server
verisium_debug_server.close()
