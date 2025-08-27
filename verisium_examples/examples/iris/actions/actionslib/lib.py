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

import argparse
from datetime import datetime
import csv
import time
import os
# TODO: Do we need to add indago library to Python Path, or we can assume users will
# always use python provided on indago install?
from indago import IndagoArgs, IndagoServer
from indago.clientpreferences import client_preferences
from indago.logflow.utils import PerfCsv
import psutil

run_dir = os.getcwd()
perf_log_path = os.path.join(run_dir, "verisium_debug_logs/perf.log")
perf_csv_path = os.path.join(run_dir, "verisium_debug_logs/perf.csv")
anon_perf_log_path = os.path.join(run_dir, "verisium_debug_logs/anon_perf.log")
objects_dict_path = os.path.join(run_dir, "verisium_debug_logs/objects_dict.csv")
result_csv_path = os.path.join(run_dir, "verisium_debug_logs/result.csv")
metadata_json_path = os.path.join(run_dir, "verisium_debug_logs/metadata.json")
indago_args = None


class ActionParameters:
    '''Parameters used by base_action'''
    def __init__(self, arguments):
        self.db_path = arguments.db_path
        self.indago_root = arguments.indago_root
        self.extra_args = arguments.extra_indago_args
        self.objects_dict_path = arguments.objects_dict_path
        self.anonymize = arguments.anonymize
        self.indago_window_size = arguments.indago_window_size
        self.test_count = arguments.test_count
        self.disable_validation = arguments.disable_validation
        self.set_timeout = arguments.set_timeout

def parse_actions_arguments(description):
    '''Parse parameters function'''
    # Inputs:
    # db_path = path to db, e.g.: "/dv/p4users09il/aeraf/aeraf_agile_ida_ps3/rflow_test/regression_designs32/uvm_clab_parity/ida.db/"
    # indago_root = path to indagoRoot, e.g.: "/dv/p4users09il/aeraf/aeraf_agile_ida_ps3/dvproject/dep"
    # extra_args = extra indago args, e.g.: "-nolwd -nsp -64bit -tcl input.tcl"
    # objects_dict_path = path to a file
    # anonymize - on or off
    args = argparse.ArgumentParser(
        description = 'This is one of the predefined actions.py files to measure Indago performance. ' +
                      f'Should be used with Performance Core Script. {description}',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Required arguments
    # TODO: Handle case of multiple dbs
    args.add_argument('db_path', type=str, help='path to db (usually ida.db)')
    # TODO: indago_root should be an optional argument
    args.add_argument('indago_root', type=str, help='path to Indago root (usually $INDAGO_ROOT)')

    # Optional arguments
    args.add_argument('--extra_indago_args', type=str, required=False, default=None, help='Extra Indago launch arguments, for example, "-nolwd -nsp -64bit -tcl input.tcl"')
    args.add_argument('--objects_dict_path', type=str, required=False, default=None, help='Path to objects dict csv file')
    args.add_argument('--anonymize', choices=['True', 'False'], required=False, default=False, help='Define if perf.log/perf.csv should be anonymized')
    args.add_argument('--disable_validation', required=False, default=False, action='store_true', help='Define if objects_dict.csv should be validated')
    args.add_argument('--set_timeout', type=int, required=False, default=10, help='Define timeout in minutes for objects_dict.csv creation')
    # TODO: define expected format for windows size
    args.add_argument('--indago_window_size', type=str, required=False, default=None, help='Windows size to be used when launching indago')
    args.add_argument('--test_count', type=int, default=1000, help='Set up how many times each call will be tested.', required=False)

    # Parse arguments
    action_parameters = ActionParameters(args.parse_args())
    # TODO: Handle case of multiple dbs
    # TODO: Handle the default usage for indago_root were we get it from env var INDAGO_ROOT
    # TODO: Check if all arguments are valid (paths exist, objectsDict is valid, etc.)
    return action_parameters


def launch_indago(db_path, indago_root, extra_args, indago_window_size):
    global indago_args
    # TODO: Implement option to define indago window size
    # TODO: When available, we should have an additional fixed extra_args to turn
    # on performance measurement
    if db_path.split("/")[-1] == "xcelium.d":
        client_preferences.close_servers_at_exit = False
        indago_args = IndagoArgs(indago_root=os.path.expandvars(indago_root)+'/bin/indago',
                                 is_gui=True,
                                 lwd=os.path.expandvars(db_path),
                                 extra_args=extra_args)
    else:
        indago_args = IndagoArgs(indago_root=os.path.expandvars(indago_root)+'/bin/indago',
                                 is_gui=True,
                                 db=os.path.expandvars(db_path),
                                 extra_args=extra_args)

    indago_server = IndagoServer(indago_args)
    # TODO: Add some sanity check for the launch process
    return indago_server


def anonymize_perf_log(objects_dict_list, anonymize):
    '''This method anonymize the perf.log using the objects_dict as reference'''
    if anonymize == 'True':
        # TODO: Do some sanity check if objectsDictPath is readable and in the expected format,
        # and if it is not, decide how we want to fail: ignore it and create new randomly or fail?
        # 1 open perf.log
        with open(perf_log_path, 'r') as perf_file:
            perf_log_file = perf_file.read()

            # 2 replace objects_dict in perf.log
            missing_signals = []
            for obj_item in objects_dict_list:
                current_key = ''
                if obj_item['actionName'] == 'showFile':
                    current_key = os.path.basename(obj_item['key'])
                else:
                    current_key = obj_item['key']

                if perf_log_file.find(current_key) > 0:
                    perf_log_file = perf_log_file.replace(current_key, obj_item['id'],1)
                else:
                    print(f'sinal not found: {current_key}')
                    missing_signals.append(current_key)

            # 3 save anon_perf.log in a new file
            new_anon_perf = perf_log_file
            with open(anon_perf_log_path, 'w', encoding='utf-8') as anon_file:
                anon_file.write(new_anon_perf)

            if len(missing_signals) == 0:
                print('Annonimyze completed')
            else:
                print(f'Annonimyze failed. Do a manual check for sensitive data.\nSignals not found: {len(missing_signals)}')


def close_indago(indago_server, pid):
    print("Closing Verisium server")
    indago_server.close()
    check_and_kill_pid(pid)


def check_and_kill_pid(pid):
    """ Check For the existence of a unix pid. """
    # TODO: need a way to check the real PID of INDAGO
    try:
        time.sleep(30)
        if psutil.pid_exists(int(pid)):
            print(f'Killing verisium process PID {pid}')
            os.kill(pid, 0)
    except OSError as e:
        # TODO: Log error
        print(f"check_and_kill_pid - OSError: {e}")
        return False
    except Exception as e:
        print(f"check_and_kill_pid - Exception: {e}")
        # TODO: log error
        return False
    else:
        # TODO: Log status
        print(f"check_and_kill_pid - kill with success")
        return True


def print_progress(message, counter):
    if counter == 0 or (counter + 1) % 50 == 0:
        print (f'{message}: {counter+1}')


def check_indago_online(pid):
    '''Checks if the informed Verisium PID is running'''
    # TODO: logging error
    if psutil.pid_exists(pid):
        print(f'INDAGO Online - PID {pid}')
    else:
        print(f'Exiting. INDAGO is not online with PID {pid}')
        exit()
