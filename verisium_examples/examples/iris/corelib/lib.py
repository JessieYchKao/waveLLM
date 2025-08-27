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
''' Define documentation for the lib.py'''

import argparse
import logging
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
from time import time, sleep
from typing import List
import csv
from corelib.log_helper import print_and_log
from pyvirtualdisplay import Display

class CoreParameters:
    ''' CoreParameters is responsible to verify the values used as parameters '''

    error_list: List[str] = []

    def __init__(self, arguments):
        self.db_path = os.path.expandvars(arguments.db_path) if arguments.db_path else None
        self.indago_root = os.path.expandvars(arguments.indago_root) if arguments.indago_root else None
        self.actions_path = os.path.expandvars(arguments.actions_path) if arguments.actions_path else None
        self.xrun_path = os.path.expandvars(arguments.xrun_path) if arguments.xrun_path else None
        self.run_dir = os.path.expandvars(arguments.run_dir) if arguments.run_dir else None
        self.session_output_path = os.path.expandvars(arguments.session_output_path) if arguments.session_output_path else None
        self.extra_indago_args = arguments.extra_indago_args
        self.objects_dict_path = arguments.objects_dict_path
        self.anonymize = arguments.anonymize
        self.extra_env = arguments.extra_env
        self.display_path = arguments.display_path
        self.indago_window_size = arguments.indago_window_size
        self.test_count = arguments.test_count
        self.disable_validation = arguments.disable_validation
        self.debug_mode = arguments.debug_mode
        self.log_parameters()

    def __str__(self):
        return str(self.__dict__)

    def log_parameters(self):
        '''Log used parameters'''
        for param_name, param_value in self.__dict__.items():
            logging.debug(' %s: %s', param_name, param_value)

    def validate_args(self):
        '''Check if required and optional parameters are valid'''
        logging.info('Starting parameter validation')
        self.check_req_arg()
        self.check_opt_arg()

        if len(CoreParameters.error_list) > 0:
            logging.error('Parameter validation failed')
            for item in CoreParameters.error_list:
                logging.error(item)
            print("\nExecution failed:\n" + "\n".join(CoreParameters.error_list))
            sys.exit(1)
        logging.info('Parameter validation passed')

    def check_req_arg(self):
        ''' Validate required arguments '''
        CoreParameters.path_validator('db_path', self.db_path)
        CoreParameters.executable_validator('indago_root', self.indago_root + '/bin/indago', '-version')
        CoreParameters.file_validator('actions_path', self.actions_path)
        CoreParameters.executable_validator('xrun_path', self.xrun_path + '/xrun', '-version')
        CoreParameters.folder_permission_validator('self.run_dir',self.run_dir,)
        CoreParameters.folder_permission_validator('self.session_output_path',self.session_output_path)

    def check_opt_arg(self):
        ''' Validate optional arguments '''
        if self.objects_dict_path is not None:
            CoreParameters.file_validator('objects_dict_path',self.objects_dict_path)
            if not CoreParameters.param_has_error('objects_dict_path'):
                with open(self.objects_dict_path, mode='r') as csvfile:
                    reader = list(csv.reader(csvfile, delimiter=','))
                    # looking into csv for this structure: <row_number>,<id>,<object full path>,<object type>,<action name>
                    if reader is None or len(reader[0]) is not 5:
                        CoreParameters.add_error(f'Invalid parameter objects_dict_path. The value {self.objects_dict_path} must came in pairs.')

        if self.anonymize is not None:
            if self.anonymize not in (True, False):
                CoreParameters.add_error('Invalid parameter anonymize')

        if self.display_path is not None and not is_valid_display(self.display_path):
            CoreParameters.add_error(f'Invalid parameter display_path. The value {self.display_path} does not exists or it\'s not accesible.')

        if self.indago_window_size is not None:
            try:
                w_size = self.indago_window_size.split()
                if len(w_size) != 2 or (not isinstance(int(w_size[0]), int) or not isinstance(int(w_size[1]), int)):
                    CoreParameters.add_error("Invalid indago_window_size. It should be int int.")
            except:
                CoreParameters.add_error("Invalid indago_window_size. It should be int int.")

        if self.extra_env is not None:
            if len(self.extra_env) > 0:
                for item in self.extra_env:
                    if len(item.split()) is not 2:
                        CoreParameters.add_error("Invalid parameter extra_env.")

    @classmethod
    def path_validator(cls, param_name: str, path_value: str):
        ''' Validate if the path informed is valid or not
        Args:
        param_name (str): Parameters name.
        path_value (str): The path to be checked. Can contain Enviornment variables
        '''
        logging.info('Validating parameter %s - %s', param_name, path_value)
        if path_value is None or not os.path.exists(os.path.expandvars(path_value)):
            cls.error_list.append(f'Invalid parameter {param_name}. The path "{path_value}" does not exists or is not accessible')

    @classmethod
    def folder_permission_validator(cls, param_name: str, path_value: str):
        ''' Validate if the path informed is valid and has write permissions
        Args:
        param_name (str): Parameters name.
        path_value (str): The path to be checked. Can contain Enviornment variables
        '''
        logging.info('Validating parameter %s - %s', param_name, path_value)
        CoreParameters.path_validator(param_name, path_value)
        if path_value is None or not os.access(os.path.expandvars(path_value), os.W_OK):
            cls.error_list.append(f'Invalid parameter {param_name}. The path "{path_value}" does not have write permissions')

    @classmethod
    def file_validator(cls, param_name: str, file_path: str):
        ''' Validate if the file informed is valid or not
        Args:
        param_name (str): Parameters name.
        file_path (str): Path to the file. Can contain Enviornment variables
        '''
        logging.info('Validating parameter  %s - %s', param_name, file_path)
        if file_path is None or not os.path.isfile(os.path.expandvars(file_path)):
            cls.error_list.append(f'Invalid parameter {param_name}. The file {file_path} does not exists or is not accessible')

    @classmethod
    def executable_validator(cls, app_name: str, app_path: str, *app_args: str):
        ''' Validate if the executable exists and runs
        Args
        app_name (str): Application name
        app_path (str): full path to the application. Can contain Enviornment variables
        app_args (list): A list of parameters to be tested
        '''
        logging.info(f'Validating parameter {app_name} - {app_path} {" ".join(map(str,app_args))}')
        try:
            # if execution fails, a CalledProcessError exception will be raised
            subprocess.run(app_path + ' ' + " ".join(map(str,app_args)), shell=True, capture_output=True, text=True, check=True) #working version
        except subprocess.CalledProcessError as e:
            cls.error_list.append(f'Invalid parameter {app_name}. Failed to run {app_path} {" ".join(map(str,app_args))} command. It does not exist or it\'s not accessible.\n' +
                                  f'Return Code: {e.returncode}, Output: {e.output}')

    @classmethod
    def param_has_error(cls, param_name):
        ''' Check if the informed parameter was already marked with error'''
        if param_name in cls.error_list:
            return True
        return False

    @classmethod
    def add_error(cls, message: str):
        cls.error_list.append(message)

def parse_core_script_arguments():
    # Inputs:
    # db_path = path to db, e.g.: "/dv/p4users09il/aeraf/aeraf_agile_ida_ps3/rflow_test/regression_designs32/uvm_clab_parity/ida.db/"
    # indago_root = path to indagoRoot, e.g.: "/dv/p4users09il/aeraf/aeraf_agile_ida_ps3/dvproject/dep"
    # extra_args = extra indago args, e.g.: "-nolwd -nsp -64bit -tcl input.tcl"
    # objects_dict_path = path to a file
    # anonymize - on or off
    # actions_path = "/dv/p4users09il/aeraf/aeraf_agile_ida_ps3/rflow_test/idao_gui_test/env/scripts/iris/actions/actions_send_to_wave.py"
    # xrun_path = "/dv/project/agile/indago/dep.342341.03Mar22_075129/agile/indago/approved/install/tools/bin"
    # extra_env_vars = "-extraEnvVars INDAGO_DEV 1 -extraEnvVar PATHTOBLA /home/bla/"
    # run_dir = "/home/aeraf/bla/test"
    # session_output_path = "/home/aeraf/bla/sessionOutput"
    # display_path = vltpk-aeraf:3

    HELP_MESSAGE = dict([
        ('db_path', 'Path to db (usually ida.db)'),
        ('indago_root', 'Path to Indago root (usually $INDAGO_ROOT'),
        ('actions_path', 'Path to actions.py to run'),
        ('xrun_path', 'Path to xrun dir (usually finishes with /install/tools/bin)'),
        ('run_dir', 'Path to temporary directory to run tests'),
        ('session_output_path', 'Path to permanent directory to store run results'),
        ('--extra_indago_args', 'Extra Indago launch arguments, for example, "-nolwd -nsp -64bit -tcl input.tcl"'),
        ('--objects_dict_path', 'Path to objects dict csv file'),
        ('--anonymize', 'Define if perf.log/perf.csv should be anonymized'),
        ('--extra_env', 'Extra environment variables to be defined before test run. usage "env_var_name env_var_value". For multiple env vars, pass this switch multiple times.'),
        ('--display_path', 'Path to display to be used to run test'),
        ('--indago_window_size', 'Windows size to be used when launching indago'),
        ('--test_count', 'Define the number of the repetitions the actions script will execute'),
        ('--disable_validation', 'Disable the objects_dict validation'),
        ('--debug_mode', 'Set the ���-debug_logger high" parameter for the current Verisium Debug run and copy all files from the temporary folder to the output folder'),
    ])

    logging.info('Parsing argumnts')

    # TODO: A lot of love required to improve this help
    ap = argparse.ArgumentParser(description='Core Script to evaluate Indago Peformance.',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Required arguments
    ap.add_argument('db_path', type=str, help=HELP_MESSAGE['db_path'])
    # TODO: Indago_root should be an optional argument
    ap.add_argument('indago_root', type=str, help=HELP_MESSAGE['indago_root'])
    ap.add_argument('actions_path', type=str, help=HELP_MESSAGE['actions_path'])
    ap.add_argument('xrun_path', type=str, help=HELP_MESSAGE['xrun_path'])
    ap.add_argument('run_dir', type=str, help=HELP_MESSAGE['run_dir'])
    ap.add_argument('session_output_path', type=str, help=HELP_MESSAGE['session_output_path'])

    # Optional arguments
    ap.add_argument('--extra_indago_args', type=str, required=False, default=None, help=HELP_MESSAGE['--extra_indago_args'])
    ap.add_argument('--objects_dict_path', type=str, required=False, default=None, help=HELP_MESSAGE['--objects_dict_path'])
    ap.add_argument('--anonymize', required=False, default=False, action='store_true',  help=HELP_MESSAGE['--anonymize'])
    ap.add_argument('--extra_env', type=str, action='append', required=False, default=None, help=HELP_MESSAGE['--extra_env'])
    ap.add_argument('--display_path', type=str, required=False, default=None, help=HELP_MESSAGE['--display_path'])
    ap.add_argument('--indago_window_size', type=str, required=False, default=None, help=HELP_MESSAGE['--indago_window_size'])
    ap.add_argument('--test_count', type=int, required=False, default=1000, help=HELP_MESSAGE['--test_count'])
    ap.add_argument('--disable_validation', required=False, default=False, action='store_true',  help=HELP_MESSAGE['--disable_validation'])
    ap.add_argument('--debug_mode', required=False, default=False, action='store_true',  help=HELP_MESSAGE['--debug_mode'])

    # Parse arguments
    core_parameters = CoreParameters(ap.parse_args())

    # Validate arguments
    core_parameters.validate_args()

    return core_parameters


def define_temp_run_dir(run_dir):
    # TODO: Do we expect to have a default to be the current run dir?
    # Create an empty folder inside of run dir using timestamp
    timestamp = str(time()).replace('.', '')
    full_run_dir = os.path.join(os.path.expandvars(run_dir), timestamp)
    mkdir_cmd = 'mkdir ' + full_run_dir
    try:
        subprocess.run(mkdir_cmd, shell=True, check=True)
        os.environ["INDAGO_TEMP_DIR"] = full_run_dir
        os.environ["INDAGO_USER_HOME"] = full_run_dir
        os.environ["INDAGO_SCRIPTING_NO_PG_KILL"] = "1"
        print_and_log(f'Temporary run_dir directory created at {full_run_dir}',logging.INFO)
    except Exception as ex:
        print_and_log(f'Process failed while creating temporary run_dir directory: {ex}', logging.ERROR)
        sys.exit(1)

    return full_run_dir


def set_environment(xrun_path, indago_root, extra_env):
    # TODO: Here we should have three options: start with clean environment and set everything,
    # start with same environment from the current user or
    # clean but keep some predefined env vars from user env
    my_env = os.environ.copy()
    # Add xrun to path
    my_env["PATH"] = os.path.expandvars(xrun_path) + ':' + my_env["PATH"]
    # Create INDAGO_ROOT
    my_env["INDAGO_ROOT"] = os.path.expandvars(indago_root)

    # TODO: PYTHONPATH is needed to point to our library?
    # Set extra env vars
    if extra_env is not None:
        for env_pair in extra_env:
            my_env[env_pair[0]] = env_pair[1]
    return my_env


def is_valid_display(display_path):
    '''Check if the informed display is valid or not'''
    try:
        # if execution fails, a CalledProcessError exception will be raised
        subprocess.run(['xdpyinfo', '-display', display_path], check=True, capture_output=True, text=True)
        os.environ["DISPLAY"] = display_path
        return True
    except subprocess.CalledProcessError:
        logging.error('Invalid display %s. It does not exist or it\'s not accessible.', display_path)
        return False


def define_display(display_path):
    if display_path is None:
        logging.info("Creating Display")
        display_list = ['xvfb', 'xvnc', 'xephyr']
        for disp_type in display_list:
            try:
                virtual_display = Display(visible=True, backend=str(disp_type), size=(1920, 1080))
                virtual_display.start()
                if virtual_display.is_alive():
                    logging.info('Display created')
                    return virtual_display
            except:
                logging.debug('Display %s not avaliable', disp_type)
            else:
                logging.debug('Display %s not avaliable', disp_type)

        logging.error("Display could not be created")
        sys.exit(1)


def run_actions(args, my_env, full_run_dir):
    # TODO: indago_root should be optional parameter
    cmd = args.indago_root + '/tools/indago/scripting/python/bin/python -u ' + args.actions_path + ' ' + args.db_path + ' ' + args.indago_root
    if args.extra_indago_args is not None and " -memlimit 256G -performance" not in args.extra_indago_args:
        args.extra_indago_args += " -memlimit 256G -performance"
    if args.extra_indago_args is None:
        args.extra_indago_args = " -memlimit 256G -performance"
    if args.debug_mode is True:
        args.extra_indago_args = ''.join([args.extra_indago_args, ' -debug_logger high'])
    cmd += ' --extra_indago_args "' + args.extra_indago_args + '"'
    if args.objects_dict_path is not None:
        cmd = ''.join([cmd,' --objects_dict_path ', args.objects_dict_path])
    if args.anonymize:
        cmd = ''.join([cmd,' --anonymize ', str(args.anonymize)])
    if args.disable_validation is True:
        cmd = ''.join([cmd,' --disable_validation '])
    cmd = ''.join([cmd, ' --test_count ', str(args.test_count)])

    logging.info('running action: %s', cmd)

    print(f'CurrentAction: {args.actions_path}')
    print(f'CurrentDB: {args.db_path}')
    print(f'Command Received corelib/lib.py: {cmd}')

    # TODO: We need a better way to catch and threat exceptions, eg: print, logging, return code, etc
    try:
        # process = subprocess.run(os.path.expandvars(cmd), shell=True, env=my_env, cwd=full_run_dir, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        has_exception = False
        process = subprocess.Popen(os.path.expandvars(cmd), shell=True, env=my_env, cwd=full_run_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                if "Traceback" in output:
                    has_exception = True
                if has_exception:
                    logging.error(output.replace('\n',''))
                else:
                    logging.info(output.replace('\n',''))
                print(output, end="")
    except Exception as ex:
        print('Exception ERROR_RUNNING_ACTION')
        print_and_log(ex, logging.ERROR)
        return 1
    finally:
        output = process.communicate()[0]
        if output != '':
            print_and_log(output, logging.INFO)
        return process.returncode

def clean_temp_dir(temporary_run_dir_path):
    '''
    Delete the folder that is created under the temporary path informed
    Args:
    temporary_run_dir_path (str): directory to be cleaned
    '''
    logging.info('Cleaning up temporary folder: %s', temporary_run_dir_path)
    for i in range(5):
        if os.path.exists(temporary_run_dir_path):
            print(f'Cleaning up temporary folder {i}: {temporary_run_dir_path}')
            shutil.rmtree(temporary_run_dir_path, ignore_errors=False, onerror=handle_error)
        i += 1
        sleep(0.5)


def handle_error(func, path, exc_info):
    '''
    Error handler function
    It will try to change file permission and call the function again,
    '''
    logging.error('Fail to clean up the run dir: %s', path)
    logging.error('Error details: %s', exc_info)

    # Check if file access issue
    if os.path.exists(path) and not os.access(path, os.W_OK):
        # Try to change the permision of file
        os.chmod(path, stat.S_IWUSR)
        # call the calling function again
        if os.path.exists(path):
            func(path)


def create_output_dir(output_dir, action_name, db_path):
    '''Create a directory to save relevant files from the execution.
    Args:
    output_dir (str): base output dir informed while calling core_script
    action_name (str): Path to the current action file
    db_path (str): Path to the design used'''

    logging.info('Creating output folder structure')
    logging.debug(f'Received Parameters: Output: {output_dir} - Action: {action_name} - DBPath: {db_path}')

    action_name = os.path.splitext(os.path.basename(action_name))[0]

    # TODO: This part is hardcoded. Maybe there is a better way to get the design name
    if '/grid/ida/design/CAT_designs/' in db_path:
        design_name = Path(db_path).parts[5]
    else:
        design_name = os.path.basename(os.path.dirname(db_path))
    timestamp = str(time()).replace('.', '')

    folder_destination = f'{output_dir}/{action_name}/{design_name}/{timestamp}'
    os.makedirs(folder_destination)
    if os.path.exists(folder_destination) is False:
        logging.error('Failed to create temporary directory')
        return None

    print(f'Output Folder Created: {folder_destination}')
    logging.info('Output folder created successfully')
    return folder_destination

def save_all_logs(temporary_run_path, folder_destination):
    '''Save all files/logs generated during the IRIS execution
    Args:
    annonymize (bool): flag to inform that the anonymize file sholud be copied
    temporary_run_dir_path (str): path to look for the files
    folder_destination (str): final destination where the files should be copied'''

    try:
        # if execution fails, a CalledProcessError exception will be raised
        shutil.copytree(temporary_run_path, folder_destination + '/all_debug_files', ignore=shutil.ignore_patterns('.simvision','.java'))
        return True
    except Exception as ex:
        logging.error('Fail to copy the temporary folder: %s.', temporary_run_path)
        logging.error('Error: %s.', ex)
        return False


def save_relevant_logs(anonymize, temporary_run_dir_path, folder_destination, debug_mode = False):
    '''Save all relevant files/logs generated during the IRIS execution
    Args:
    annonymize (bool): flag to define which file sholud be copied
    temporary_run_dir_path (str): path to look for the files
    folder_destination (str): final destination where the files should be copied'''

    logging.info('Copying relevant logs')

    if folder_destination is None or os.path.exists(folder_destination) is False:
        logging.warning('Temporary folder unavaliable. Unable to copy relevant logs')
        return

    if debug_mode is True:
        logging.info("Debug_mode enable. Copying all files from temporary folder.")
        save_all_logs(temporary_run_dir_path, folder_destination)

    list_of_files_to_copy = ['command.history',
                             'history.py',
                             'ida.log',
                             'verisium_debug_lwd.log',
                             'verisium_debug_karaf.log', # only appear when debug is enabled (optional)
                             'verisium_debug.log',
                             'perf.csv', # required
                             'perf.log', # required
                             'metadata.json', # required
                             'session_info',
                             'objects_dict.csv', # required
                             'result.csv' # required
                             ]

    if anonymize:
        logging.info('Processing anonymized files')
        # TODO: Add files that should not be copied or must have
        # a different behavior if annonymize parameter is True
        # list_of_files_to_copy.remove('perf.log')
        list_of_files_to_copy.append('anon_perf.log')

    for file in list_of_files_to_copy:
        try:
            shutil.copy2(temporary_run_dir_path + '/verisium_debug_logs/' + file, folder_destination)
            logging.info('File %s copied to the output dir', file)
        except OSError:
            if file in ['perf.csv', 'perf.log', 'metadata.json', 'objects_dict.csv']:
                logging.error('Failed to copy required file %s', file)
            else:
                logging.warning('File %s was not copied.', file)
        except:
            logging.error('Unexpected error: %s', sys.exc_info()[0])

