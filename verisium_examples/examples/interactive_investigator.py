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

# This interactive investigator will allow the user to launch a client connected to an Verisium Debug Server
# and explore the designs contents.  It will prompt the user for a regex expression and a depth and
# then search through the design, returning module name hits that match the users search criteria.
# Once the hits are found, it will then print them to the screen and prompt the user to pick one to
# print the ports and signals for it.  It will then prompt the user for a signal to explore in more
# detail, then offering the ability to trace drivers, print all signal values, or only print X or Z
# values.
# At each prompt, the user can select b to go back to the previous prompt or -1 to exit the script.

from verisium import *
import sys, os

def get_top_scopes(verisium_debug_server = None):
    ''' This method will return the top level scopes of an input Verisium Debug Server '''
    top_scopes = verisium_debug_server.scopes()
    return top_scopes

def get_user_modules(verisium_debug_server = None, regex_string = None, depth = None):
    ''' This method will return the user requested modules '''
    module_hits = verisium_debug_server.scopes(ct.depth <= depth, ct.declaration_name.matches(regex_string))
    return module_hits

def get_ports_for_instance(instance = None):
    ''' This method will return the ports for an instance passed in by the user'''
    instance_ports = instance.ports()
    return instance_ports

def print_ports(ports = None):
    ''' This method will print all of the important fields of a list of ports '''
    for i, p in enumerate(ports):
        print("\t[" + str(i) + "] \t" + p.name + ", " + str(p.direction) + ", " + str(p.size))

def get_signals_for_instance(instance_scope = None):
    ''' This method will return all of the signals for an Scope object passed in by the user'''
    instance_signals = instance_scope.signals()
    return instance_signals

def print_signals(signals = None):
    ''' This method will print all of the important fields of a list of Signal Class objects '''
    for i, s in enumerate(signals):
        #print(s)
        print("\t[" + str(i) + "] \t" + s.name + ", " + s.type.name + ", " + str(s.size) + ", " + str(s.source.file) + ", " + str(s.source.line_start))

def get_drivers_for_signal(signal = None):
    ''' This method will return all of the drivers for a signal Class object passed in by the user'''
    drivers = signal.drivers()
    return drivers

def print_drivers_for_signal(drivers = None):
    ''' This method will print all of the important fields of a list of Driver objects, including their contributors '''
    for i, d in enumerate(drivers):
        print("\n")
        #print(d)
        print("\t[" + str(i) + "] \t" + d.name + ", " + str(d.source.file) + ", " + str(d.source.line_start))

        # Get and print the contributor information for each driver
        print("\tContributors: ")
        contributors = d.contributors()

        print("\n".join("\t\t" + c.name + ", " + c.type.name + ", " + str(c.size) + ", " + str(c.source.file) + ", " + str(
            c.source.line_start) for c in contributors))

def get_values_for_signal(verisium_debug_server = None, signal = None):
    ''' This method will retrieve all of the recorded signals values in the values_database for verisium_debug_server.
        As we can never be sure of when recording was turned on/off during the simulation, we must query the
        values_database within the verisium_debug_server for it's start and end times, then pass those values to the
        corresponding API call to get the values
    '''
    # Identify the start and end times of the recorded simulation database
    start_time = verisium_debug_server.server_info.values_databases[0].start
    end_time = verisium_debug_server.server_info.values_databases[0].end
    signal_values = signal.values(ct.start_time == start_time, ct.end_time == end_time)
    return signal_values

def print_signal_values(signal = None, values = None):
    ''' This method will print all of the TimeValue objects passed in from the user
    '''
    for i, val in enumerate(values):
        print("\t[" + str(i) + "] \t" + str(val.time.time) + ", " + val.value)

def get_x_values(values = None):
    ''' This method will print all occurrences of x or X on a signal '''
    x_values = [tv for tv in values if (('x' or 'X') in tv.value)]
    return x_values

def get_z_values(values = None):
    ''' This method will print all occurrences of z or Z on a signal '''
    z_values = [tv for tv in values if (('z' or 'Z') in tv.value)]
    return z_values

def launch_verisium_debug_server():
    '''
    This method is used to establish a connection to a VerisiumDebugServer.  The user will be prompted
    for a database name to connect to and then,will establish that connection and return the
    verisium debug server to the user
    :return: A VerisiumDebugServer class, connected to a design
    '''

    # Instantiate a new verisium debug arguments Class
    verisium_debug_args = VerisiumDebugArgs()

    # Get the name of the database to connect to from the user
    input_db_name = input("\nPlease enter the path to a recorded simulation database (SHM file) (ex: /hm/user/design/ida.db/ida.shm): ")

    # Strip away any extra whitespace
    verisium_debug_args.db = input_db_name.strip()

    # simple check that the user typed in a good path.
    if not os.access(verisium_debug_args.db, os.R_OK):
        print ("\nERROR: Can't find the database: "+verisium_debug_args.db +", Please check to ensure this path is valid and the file exists.")
        close_verisium_debug_server(verisium_debug_server)
        sys.exit(1)

    # launch Verisium Debug and establish a connection to it. this connection is represented by the VerisiumDebugServer object
    # instance verisium_debug_server.
    try:
        verisium_debug_server = verisiumdebugserver.VerisiumDebugServer(verisium_debug_args)
    except:
        print("\nERROR: Failed to connect to VerisiumDebugServer with the following arguments (please check the database format and try again):"+str(verisium_debug_args))
        close_verisium_debug_server(verisium_debug_server)
        sys.exit(1)
    else:
        print("\nVerisiumDebugServer successfully connected. Here is a print of the ServerInfo object: \n"+str(verisium_debug_server.server_info))

    return verisium_debug_server


def interactive_investigate(verisium_debug_server = None):
    ''' This interactive investigator will alow the user to launch a client connected to a Verisium Debug Server
    and explore the designs contents.  It will prompt the user for a regex expression and a depth and
    then search through the design, returning module name hits that match the users search criteria.
    Once the hits are found, it will then print them to the screen and prompt the user to pick one to
    print the ports and signals for it.  It will then prompt the user for a signal to explore in more
    detail, then offering the ability to trace drivers, print all signal values, or only print X or Z
    values. At each prompt, the user can select b to go back to the previous prompt or -1 to exit the script.
    :param verisium_debug_server: The server that will be used to extract values from
    :return: None
    '''

    # Get all the top-level scopes of the design loaded into the server
    top_level_scopes = get_top_scopes(verisium_debug_server)

    # If nothing is returned for top level scopes, no need to proceed, exit
    if top_level_scopes is None:
        print("ERROR: get_top_scopes() method returned no scopes.  Exiting")
        close_verisium_debug_server(verisium_debug_server)
        sys.exit(1)

    # next_module is used to disable this while loop and exit the program if needed
    next_module = True
    # Loop continuously, allowing the user to search for multiple regex/depth combinations
    while (next_module == True):

        # If we find some top level scopes, print them, else emit a warning
        if (len(top_level_scopes) > 0):
            print("\n\nFound "+str(len(top_level_scopes))+" Top level scopes: \n"+"\n".join("\t"+t.full_path for t in top_level_scopes))
        else:
            print("\nWARNING: No top level scopes found in: "+verisium_debug_args.db)

        # Aquire a regular expression from the user for the module name
        module_name = ''
        while (module_name is ''):
            module_name = input("\nPlease enter a regular expression for a module to search for instances on (e.g. *my_module$) : ")
            # Validate the user input to ensure it has something and that "something"
            # is not just a number.  If we don't receive what we expect, null the input
            # and prompt the user again
            if (module_name is not ''):
                if (module_name.isnumeric()):
                    module_name = ''
                else:
                    module_name = module_name.strip()

        # Aquire a depth from the user for which to search
        depth = ''
        while (depth is ''):
            depth = input("\nPlease enter a depth (0-99) to retrieve instances from (-1 to exit): ")
            # Validate the user input to ensure it has something and that "something"
            # is a valid number.  If we don't receive what we expect, null the input
            # and prompt the user again
            if (depth is not ''):
                if (int(depth) in range(-1,100)):
                    depth = int(depth.strip())
                    # Exit if the user so wishes
                    if (depth == -1):
                        close_verisium_debug_server(verisium_debug_server)
                        sys.exit(0)
                else:
                    depth = ''

        # Extract what the user requested and, if None Type is returned, throw an exception
        try:
            # Return all the user requested modules back for further processing
            module_instances = get_user_modules(verisium_debug_server, module_name, depth)
        except:
            print("ERROR: get_user_modules("+module_name+","+str(depth)+") returned None type, meaning no hits were found.")

        # Now, check whether there are any hits and print them to the screen
        if ('module_instances' in vars() and len(module_instances) > 0):
            print("Found "+str(len(module_instances))+" instance hits for depth "+str(depth)+": ")

            # Print the hits to the screen along with their index
            for i,m in enumerate(module_instances):
                print("\t["+str(i)+"] \t"+m.full_path+" (module_name:"+m.declaration.name+")")

            # Prompt the user to select a module instance
            instance_index = ''
            while (instance_index is ''):
                instance_index = input("\nPlease select an index [0-" + str(len(module_instances) - 1) + "] to print ports and signal information (-1 to exit): ")
                # Validate the user input to ensure it has something and that "something"
                # is a valid number.  If we don't receive what we expect, null the input
                # and prompt the user again
                if (instance_index is not ''):
                    if(int(instance_index) in range(-1, len(module_instances))):
                        instance_index = int(instance_index.strip())
                        # Exit if the user wishes
                        if (instance_index == -1):
                            close_verisium_debug_server(verisium_debug_server)
                            sys.exit(0)
                    else:
                        instance_index = ''
            if (instance_index is None):
                break
            else:
                # Grab the selection that the user wants
                instance = module_instances[instance_index]

                # Get the ports from the instance
                ports = get_ports_for_instance(instance)

                # If the above method call returns None type, we are in big
                # trouble as we won't be able to proceed with printing the ports
                # Tell the user about this error and exit the program
                if ports is None:
                    print("ERROR: get_ports_for_instance(...) returned None type.  Exiting.")
                    close_verisium_debug_server(verisium_debug_server)
                    sys.exit(1)

                # Loop, allowing the user to select signals from the instance, unless they choose
                # to go back in the menu list (by disabling the next_signal bool)
                next_signal = True
                while(next_signal == True):

                    # If the field 'ports' exists and there are ports to print, print them
                    if ('ports' in vars() and len(ports) > 0):
                        print("Found "+str(len(ports))+" ports for instance "+instance.full_path+": ")
                        # Print ports to the screen
                        print_ports(ports)
                    else:
                        print("Found no ports for instance: "+instance.full_path)

                    # Get the signals from the instance
                    signals = get_signals_for_instance(instance)

                    # If the above method call returns None type, we are in big
                    # trouble as we won't be able to proceed with printing the signals
                    # Tell the user about this error and exit the program
                    if signals is None:
                        print("ERROR: get_signals_for_instance(...) returned None type.  Exiting.")
                        close_verisium_debug_server(verisium_debug_server)
                        sys.exit(1)

                    # If the field 'signals' exists and there are signals to print, print them
                    if ('signals' in vars() and len(signals) > 0):
                        print("Found "+str(len(signals))+" signals for instance "+instance.full_path+": ")

                        # Print the signals found to the screen
                        print_signals(signals)

                        # Prompt the user to select a signal to operate on
                        signal_index = ''
                        while (signal_index is ''):
                            signal_index = input("\nPlease select a signal index [0-"+str(len(signals)-1)+"] to perform an operation on (b to go back, -1 to exit): ")
                            # Validate the user input to ensure it has something and that "something"
                            # is a valid number.  If we don't receive what we expect, null the input
                            # and prompt the user again
                            if (signal_index is not ''):
                                # If the user wants to go back in the menu, set the index to None
                                # and this will be caught a few lines down
                                if (signal_index in ('b','B')):
                                    signal_index = None
                                    break
                                elif (int(signal_index) in range(-1, len(signals))):
                                    signal_index = int(signal_index.strip())
                                    # Exit, if the user so wishes
                                    if (signal_index == -1):
                                        close_verisium_debug_server(verisium_debug_server)
                                        sys.exit(0)
                                else:
                                    signal_index = ''
                        # If the user wanted to go back in the menu, disable the next_signal
                        # control for the while loop and break out of this inner while
                        if (signal_index is None):
                            next_signal = False
                            break
                        else:
                            # Now that the user has selected a signal, loop through a number of operations
                            # They can do on that signal
                            next_operation = True
                            while (next_operation == True):

                                # Supported operations
                                operations = ["Trace Drivers", "Print Values", "Print x/X Values", "Print z/Z Values"]

                                # Print the operations to the screen and allow the user to choose between them
                                print('\n')
                                for i,op in enumerate(operations):
                                    print("\t["+str(i)+"] \t"+op)

                                # Prompt the user for an operation to perform
                                operation_index = ''
                                while (operation_index is ''):
                                    operation_index = input("\nPlease select an operation index [0-"+str(len(operations)-1)+"] to perform on signal "+signals[signal_index].name+" (b to go back, -1 to exit):")
                                    # Validate the user input to ensure it has something and that "something"
                                    # is a valid number (or b/B).  If we don't receive what we expect, null the input
                                    # and prompt the user again
                                    if (operation_index is not ''):
                                        if (operation_index in ('b','B')):
                                            # If the user wants to go back, set the operation index to None
                                            # This will be caught a few lines down
                                            operation_index = None
                                            break
                                        elif (int(operation_index) in range(-1, len(operations))):
                                            operation_index = int(operation_index.strip())
                                            # Exit, if the user so wishes
                                            if (operation_index == -1):
                                                close_verisium_debug_server(verisium_debug_server)
                                                sys.exit(0)
                                        else:
                                            operation_index = ''
                                # If the user wants to go back in the menu list
                                # disable the next_operation while loop controller
                                # and break out of this inner while loop
                                if (operation_index is None):
                                    next_operation = False
                                    break

                                # If the user wants to print drivers, do so
                                elif (operation_index == 0):

                                    # Get the drivers of the signal of interest
                                    drivers = get_drivers_for_signal(signals[signal_index])

                                    # If the above method call returns None type, we are in big
                                    # trouble as we won't be able to proceed with printing the drivers
                                    # Tell the user about this error and exit the program
                                    if drivers is None:
                                        print("ERROR: get_drivers_for_signal(...) returned None type.  Exiting.")
                                        close_verisium_debug_server(verisium_debug_server)
                                        sys.exit(1)

                                    # If there are drivers found, print them
                                    if('drivers' in vars() and len(drivers) > 0):
                                        # If drivers are found, print each one
                                        print("Found "+str(len(drivers))+" drivers for signal "+signals[signal_index].full_path+": ")

                                        # Print the drivers to the screen for the signal
                                        print_drivers_for_signal(drivers)
                                    else:
                                        print("No drivers found for signal "+signals[signal_index].full_path+": ")

                                # If the user wants to print values for the signal, do so
                                elif (operation_index == 1):

                                    # Return all of the signal values from the values_database of the verisium_debug_server
                                    signal_values = get_values_for_signal(verisium_debug_server, signals[signal_index])

                                    # If the above method call returns None type, we are in big
                                    # trouble as we won't be able to proceed with printing the values
                                    # Tell the user about this error and exit the program
                                    if signal_values is None:
                                        print("ERROR: get_values_for_signal(...) returned None type.  Exiting.")
                                        close_verisium_debug_server(verisium_debug_server)
                                        sys.exit(1)

                                    # Print the signal values
                                    print_signal_values(signals[signal_index], signal_values)

                                # If the user wants to print X values for the signal, do so
                                elif (operation_index == 2):

                                    signal_values = get_values_for_signal(verisium_debug_server, signals[signal_index])

                                    # If the above method call returns None type, we are in big
                                    # trouble as we won't be able to proceed with getting/printing x values
                                    # Tell the user about this error and exit the program
                                    if signal_values is None:
                                        print("ERROR: get_values_for_signal(...) returned None type.  Exiting.")
                                        close_verisium_debug_server(verisium_debug_server)
                                        sys.exit(1)

                                    # Get the X values from the signal values
                                    x_values = get_x_values(signal_values)

                                    # If the above method call returns None type, we are in big
                                    # trouble as we won't be able to proceed with printing x values
                                    # Tell the user about this error and exit the program
                                    if x_values is None:
                                        print("ERROR: get_x_values(...) returned None type.  Exiting.")
                                        close_verisium_debug_server(verisium_debug_server)
                                        sys.exit(1)

                                    # Print the x values to the screen
                                    print_signal_values(signals[signal_index], x_values)

                                # If the user wants to print Z values for the signal, do so
                                elif (operation_index == 3):

                                    signal_values = get_values_for_signal(verisium_debug_server, signals[signal_index])

                                    # If the above method call returns None type, we are in big
                                    # trouble as we won't be able to proceed with getting/printing the z values
                                    # Tell the user about this error and exit the program
                                    if signal_values is None:
                                        print("ERROR: get_values_for_signal(...) returned None type.  Exiting.")
                                        close_verisium_debug_server(verisium_debug_server)
                                        sys.exit(1)

                                    # Get the z values for the signals
                                    z_values = get_z_values(signal_values)

                                    # If the above method call returns None type, we are in big
                                    # trouble as we won't be able to proceed with printing the z values
                                    # Tell the user about this error and exit the program
                                    if z_values is None:
                                        print("ERROR: get_z_values(...) returned None type.  Exiting.")
                                        close_verisium_debug_server(verisium_debug_server)
                                        sys.exit(1)

                                    # Print the z values to the screen
                                    print_signal_values(signals[signal_index], z_values)
                                # Default catch all in case (for some strange reason) we may get to
                                # an undefined operation value.  In that case, we allow the user to
                                # try again.
                                else:
                                    print("Invalid operation index: "+str(operation_index))
                                    try_op_again = input("Would you like to try again? (Y/N): ")
                                    if (try_op_again in ("y","Y")):
                                        next_operation = True
                                    else:
                                        next_operation = False
                    else:
                        # If no signals are found, disable the while loop and go
                        # back in the menu system
                        print("Found no signals for instance: "+instance.full_path)
                        next_signal = False
                        break
        else:
            # If there are no instances found from the search criteria that the user
            # enters, allow them to try again
            try_again = input("No Hits found for regular expression: "+module_name+ ", depth: " + str(depth) + ". Try again? (Y/N): ")
            try_again = try_again.strip()
            if (try_again in ("y","Y")):
                next_module = True
            else:
                next_module = False

def close_verisium_debug_server(verisium_debug_server = None):
    ''' This method will close a verisium debug  server passed in by the caller'''
    # Close the verisium debug server
    verisium_debug_server.close()


# The main flow of the program
verisium_debug_server = launch_verisium_debug_server()
interactive_investigate(verisium_debug_server)
close_verisium_debug_server(verisium_debug_server)
