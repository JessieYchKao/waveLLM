# Copyright 2022 Cadence Design Systems, Inc. All rights reserved worldwide.
#
# This source code ("Software") is part of the Indago API package, the proprietary
# and confidential information of Cadence or its licensors, and supplied
# subject to, and may be used only by Cadence's customer in accordance with a
# previously executed agreement between Cadence and that customer ("Customer").
#
# Permission is hereby granted to such Customer to use and make copies of this
# Software to connect and interact with a Cadence Indago product from
# Customer's Python program, subject to the following conditions:
#
# - Customer may not distribute, sell, or otherwise modify the Indago API package.
#
# - All copyright notices in this Software must be maintained on all included
#   Python libraries and packages used by Customer.

# To run this script, we expect the user to do something like:
# $INDAGO_ROOT/tools/indago/scripting/python/bin/python $DV_VOBROOT/rflow_test/idao_gui_test/env/scripts/iris/core_script.py

import logging
import sys
from corelib.lib import (
    parse_core_script_arguments,
    define_temp_run_dir,
    set_environment,
    define_display,
    run_actions,
    clean_temp_dir,
    save_relevant_logs,
    create_output_dir)
from corelib.log_helper import set_logger, copy_log_output_dir

def main():
    set_logger('iris_perf')
    logging.info('Starting core_script program')
    log_path = logging.getLoggerClass().root.handlers[0].baseFilename
    print(f'Log file path is: {log_path}')

    ##### 0 - Parse arguments
    core_args = parse_core_script_arguments()

    ##### 1 - Define run dir
    temp_run_dir = define_temp_run_dir(core_args.run_dir)

    ##### 2 - Create a display if not informed
    virtual_display = define_display(core_args.display_path)

    ##### 3 - Set environment
    my_env = set_environment(core_args.xrun_path, core_args.indago_root, core_args.extra_env)

    ##### 4 - Run actions.py
    return_code = run_actions(core_args, my_env, temp_run_dir)

    ##### 5 - Check run status
    # TODO: Check status of execution. Some ideas:
    # Exit code
    # Sanity check on perf.log
    # Sanity check on perf.csv
    # actions.py dumps some success message on its log and core_script.py should check it
    # Check for exceptions on verisium_debug_logs
    # Sanity check on objects dict
    # Display creation status

    ##### 6 - Extend run metadata
    # TODO: Add more information to metadata. Things that can not be added by actions.py

    ##### 7 - Create run folder on session output path
    final_run_dir = create_output_dir(core_args.session_output_path, core_args.actions_path, core_args.db_path)

    ##### 8 - Copy relevant logs
    save_relevant_logs(core_args.anonymize, temp_run_dir, final_run_dir, core_args.debug_mode)

    ##### 8 - Clean run_dir and kill display and
    if virtual_display is not None:
        virtual_display.stop()

    clean_temp_dir(temp_run_dir)

    # 8.1 - Copy execution log and end the program
    logging.info('Ending core_script program')
    copy_log_output_dir(final_run_dir)

    sys.exit(return_code)

if __name__ == '__main__':
    main()
