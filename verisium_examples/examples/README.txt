
================================================================================
Welcome to the Verisium Debug Python API Examples
================================================================================
These small examples were designed to be basic building blocks from which
users can extend to implement custom functionality.  They are, in no way, 
a reflection of the full capabilities of the Verisium Debug python API.

================================================================================
Directory Tree 
================================================================================
Illustrated below is the directory tree and a shor explanation of the 
contents of each dir/file
.
|-- APBUART_design		           - Design that examples use
|   |-- design
|   |   `-- sim			           - Dir that stores the LWD and simulation DB's
|   |   `-- scripts		           - Dir containing run scripts for the design 
|-- README.txt			           - This file
|-- assertions			           - Dir containing assertion related examples
|   `-- assertions_extract.py  	           - Extracting all assertions within and below a scope 
|-- drivers_structural		           - Dir containing static driver tracing examples 
|   `-- drivers_structural.py  	           - Querying drivers and contributors for a list of signals 
|-- gui                                    - GUI API examples
|-- install_examples.py		           - Script used to install the examples and run the design
|-- parameters			           - Dir containing parameter related examples
|   |-- parameters_extract.py  	           - Extracting all parameters within and below a scope 
|   `-- parameters_extract_by_instance.py  - Extracting all parameters within and below a scope, 
|					     sorted by scope instance
|-- ports			           - Dir containing port related examples
|   |-- port_input_size_check.py           - Check to ensure all port high/low connections match 
|     				             the port size
|   `-- ports.py			   - Extract all ports for a scope			
|-- scopes				   - Dir containing all scope related examples
|   |-- scope_query.py			   - Example of some compound scope queries based on file 
|					      declaration, module name, etc. 
|   `-- scopes.py			   - Example of simple querying for scopes based on depth 
|    					      and specific path 
|-- signals				   - Dir containing all signal-related examples
    |-- signal_query.py			   - Example of simple signal extraction for a scope
    |-- signal_values.py		   - Example of extracting values for a number of signals  
    `-- signals_connections.py 		   - Example of extracting all connections for a set of signals
					     matching a regular expression 

================================================================================
Running the Examples: 
================================================================================

1) Copy over the examples to a local directory (outside of the Verisium Debug install
   directory: 

      %> python $INDAGO_ROOT/tools/indago/scripting/examples/install_examples.py

   The above command will copy over the release examples to the users
   current directory. 
   Note that there are two optional inputs to the install_examples.py script. 
   Usage of the script is given below: 
 
   usage: install_examples.py [-h] [--dest_dir DESTINATION_DIR]
                           [--no_run_demo_design]

   * -h: switch that opens the help for the install_examples.py script;
   * --dest_dir, -d: its onlt argument is the directory of where the
     examples should be installed (default is "./examples");
   * --no_run_demo_design, -n: when this flag is used, the examples design
     will NOT be run automatically after the examples are copied.

   For example, to copy the examples to a custom location and run the design:  
      %> python $INDAGO_ROOT/tools/indago/scripting/examples/install_examples.py 
         --dest_dir /my/special/path/to/install/examples

   If the design cannot be run for some reason (xrun not in the path) then the 
   design can be simulated after installing the examples using the following
   steps: 
      a) %> cd APBUART_design/design/sim
      b) %> ../scripts/run.csh

2) Once the design has been simulated, any example can be run using the the
   following steps: 
      %> cd <example_dir>
      %> python <example_file>.py 

   For example: 
      %> cd assertions
      %> python assertions_extract.py
