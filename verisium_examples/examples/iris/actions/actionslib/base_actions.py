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

''' Base class for actions'''

from abc import ABC, abstractmethod
import csv
from datetime import datetime
import os
import random
import sys
import time

from indago import *
from indago.logflow.utils import (
    parse_perf_log, calculate_percentile, generate_metadata
)
from actionslib.lib import (
    launch_indago, anonymize_perf_log, close_indago, parse_actions_arguments, check_indago_online, print_progress
)


run_dir = os.getcwd()
verisium_debug_logs_dir = os.path.join(run_dir, 'verisium_debug_logs')


class BaseAction(ABC):
    ''' Base class for Actions '''

    def __init__(self, description):
        args = parse_actions_arguments(description)

        self.required_objects = list()
        self.indago_server = None
        self.indago_server_pid = None
        self.objects_dict = None
        self.anonymize = args.anonymize
        self.full_path = None
        self.db_path = args.db_path
        self.indago_root = args.indago_root
        self.extra_args = args.extra_args
        self.objects_dict_path = args.objects_dict_path
        self.indago_window_size = args.indago_window_size
        self.test_count = args.test_count
        self.full_paths = []
        self.start_time = str(datetime.now())
        self.disable_validation = args.disable_validation
        self.set_timeout = args.set_timeout

    def add_required_object(self, action_name, object_type, num_objects, constraint=True):
        '''Abstract method to add the required_objects'''
        self.required_objects.append({'actionName': action_name,
                                      'objectType': object_type,
                                      'numObjects': num_objects,
                                      'constraint': constraint})

    def no_constraint(self, indago_object):
        return True

    def execute_action(self):
        '''Perfom Actions (this is specific for each all actions.py)'''
        print('Starting base_action.py')
        self.first_phase()
        self.second_phase()
        self.third_phase()
        print('Finishing base_action.py')

    def first_phase(self):
        '''Execute the first phase'''
        print('Starting First phase')
        for counter in range(5):
            try:
                print(f'Launching Verisium - Try #{counter+1}/5')
                self.indago_server = launch_indago(self.db_path, self.indago_root, self.extra_args, self.indago_window_size)
            except IndagoInternalError as ex:
                print(f'Fail to launch Verisium: {ex}')
                if counter == 4:
                    sys.exit('Unable to initialize Verisium')
            else:
                break

        check_indago_online(self.indago_server.server_info.pid)

        self.get_objects_dict()
        self.dump_objects_dict()
        print('Ending First phase')

    def second_phase(self):
        '''Execute the second phase'''
        print('Starting Second phase')
        self.current_action()
        print('Ending Second phase')

    @abstractmethod
    def current_action(self):
        '''Define the specific action to be executed'''

    def third_phase(self):
        '''Execute the third phase'''
        print('Starting Third phase')
        # TODO: Now we should anonymize perf.log using a python API method - anonymize is a input: if false, don't anonymize
        anonymize_perf_log(self.objects_dict, self.anonymize)
        parse_perf_log(verisium_debug_logs_dir)
        calculate_percentile([50, 75, 90, 97, 99], verisium_debug_logs_dir)
        generate_metadata(self.indago_server, verisium_debug_logs_dir, self.start_time)
        close_indago(self.indago_server, self.indago_server.server_info.pid)
        print('Ending Third phase')

    def get_objects_dict(self):
        ''' get_objects_dict'''
        # If we received and can read objectsDictPath, use it. If not, generate objectsDict randomly
        if self.objects_dict_path is None:
            self.objects_dict = self.generate_objects_dict()
        else:
            self.objects_dict = self.read_objects_dict_path()
            if self.disable_validation is False:
                self.objects_dict_validation()

    def read_objects_dict_path(self):
        ''' read_objects_dict_path '''
        # Format on csv: <row number>,<id>,<object full path>,<object type>,<action name>
        # Object format on python: list of dicts [{id: <int>, fullPath: <str>, objectType: <str>, actionName: <str>}, ...]
        # Read objects_dict_path file into a python dict
        objects_dict = list()
        # TODO: Do some sanity check if objectsDictPath is readable and in the expected format,
        # and if it is not, decide how we want to fail: ignore it and create new randomly or fail?
        with open(self.objects_dict_path, mode='r') as infile:
            reader = csv.reader(infile)
            for rows in reader:
                objects_dict.append({'id': rows[1], 'key': rows[2], 'objectType': rows[3], 'actionName': rows[4]})
        self.test_count = len(objects_dict)
        self.required_objects[0]['numObjects'] = len(objects_dict)
        return objects_dict

    def objects_dict_validation(self):
        # TODO: Check if all elements on objectsDict are available on Indago. If not we need to
        # replace them with equivalents. If a big number is not available, script may need to fail.
        # Scenarios:
        # 1-csv 100% valid, program continues
        # 2-csv more than 90% valid, program will fix the wrong signals, generating new one and continuing
        # 3-csv less than 90% valid, program will fail (probably the informed object_dict is wrong)
        print('Starting objects_dict_validation')
        # Step 1 - Verify if the objects dict file is the same as expected - i.e the same action names and number of objects
        object_count = {}
        for item in self.objects_dict:
            if item['actionName'] not in object_count:
                object_count[item['actionName']] = 1
            else:
                object_count[item['actionName']] += 1

        action_names = set()
        for obj in self.required_objects:
            action_names.add(obj['actionName'])

        if action_names != set(object_count.keys()):
            sys.exit(f"ERROR - actionName mismatch: Running action {action_names} but using "
                      "objects_dict csv file containing {set(object_count.keys())} signals")

        for action_name, count in object_count.items():
            for obj in self.required_objects:
                if obj['actionName'] == action_name:
                    if count != obj['numObjects']:
                        sys.exit("ERROR - numObjects value mismatch: The value passed for "
                            f"the action {action_name} ({obj['numObjects']}) and the "
                            f"number of objects found in the objects_dict ({count})")

        # Step 2 - Verifying if the objects_dict items are valid or not
        invalid_list = []
        for index, item in enumerate(self.objects_dict):
            print_progress('Validated objects', index)
            obj = self.find_object(item['objectType'], item['key'])

            if obj is None:
                invalid_list.append(index)

        invalid_objects_counter = len(invalid_list)
        if invalid_objects_counter > 0:
            print(f'Invalid Objects_dict items found: {invalid_objects_counter}')
            for invalid_item in invalid_list:
                print(self.objects_dict[invalid_item])
            # Now we have the invalid_list
            # Step 3 - Validate if the amount of invalid objects was reached
            if (invalid_objects_counter / len(self.objects_dict)) * 100 > 90:
                # exit('Invalid signals greater than 90% of total. Exiting')
                print('Invalid signals greater than 90% of total. Exiting')

            # Step 4 - Generate the amount of new valid items
            print('Generating new objects_dict items')
            new_valid_items = self.generate_objects_dict(invalid_objects_counter)
            print(*new_valid_items, sep = "\n")

            # Step 5 - Replace invalid objects for the new valid objects
            print('Replacing invalid objects_dict items')
            for position, new_item in zip(invalid_list, new_valid_items):
                self.objects_dict[position]['key'] = new_item['key']

        print('Objects_dict validation completed')

    def find_object(self, object_type, object_full_path):
        '''Search if the informed object exists'''
        obj = None
        if object_type == 'scope':
            obj = self.indago_server.scope_by_full_path(object_full_path)
        elif object_type == 'signal':
            obj = self.indago_server.signal_by_full_path(object_full_path)
        elif object_type == 'sourceFilePath':
            obj = self.indago_server.files(ct.file==object_full_path)
            if obj:
                obj = obj[0]
            else:
                obj = None
        return obj

    def generate_objects_dict(self, objects_amount = 0):
        ''' generate_objects_dict '''
        objects_dict = []
        print('Generating Objects_dict')
        # Loop on each group of requirements
        total_timeout = self.set_timeout * 60 # 10 minutes / per requirement / per 1k signals
        print(f"total_timeout: {self.set_timeout} {total_timeout}")
        objects_per_timeout = 1000 # 1k signals / per 10 minutes / per requirements

        for requirement in self.required_objects:
            if objects_amount == 0:
                objects_amount = requirement['numObjects']

            start_time = time.time()
            # increase the timeout if the objects_amount is greater than 1k
            if objects_amount > objects_per_timeout:
                total_timeout = total_timeout * (objects_amount/objects_per_timeout)

            # Loop on each required object
            for obj_count in range(0, objects_amount):
                print_progress('Generated objects', obj_count)
                valid_object = False
                # Randomly select an object an check if it obeys the requirement
                try_count = 0
                while not valid_object:
                    try_count += 1
                    indago_object_key, indago_object = self.draw_object(requirement['objectType'])
                    valid_object = requirement['constraint'](indago_object)
                    # check to avoid staying for to long searching for objects
                    current_time = time.time()
                    if current_time - start_time > total_timeout:
                        self.dump_objects_dict()
                        print(f"ERROR - Objects dict generation Timeout reached:\n"
                              f"{total_timeout/60} minutes\n Number of attempts: {try_count}\n"
                              f"Current signal: {indago_object_key if indago_object_key is not None else 'Not set'}")
                        sys.exit()
                objects_dict = self.add_to_objects_dict(obj_count, indago_object_key, requirement, objects_dict)
        return objects_dict

    # Dump csv inside verisium_debug_logs
    def dump_objects_dict(self):
        if not self.objects_dict:
            return

        print('Dumping ./verisium_debug_logs/objects_dict.csv')
        with open("verisium_debug_logs/objects_dict.csv", "w") as file:
            writer = csv.writer(file)
            row = 0
            for obj in self.objects_dict:
                writer.writerow([row, obj['id'], obj['key'], obj['objectType'], obj['actionName']])
                row = row + 1

    # Given a object_type and action_name, get a list of all keys on objects_dict
    def get_keys_from_objects_dict(self, object_type, action_name):
        '''get_keys_from_objects_dict'''
        return([obj['key'] for obj in self.objects_dict if (obj['objectType'] == object_type and obj['actionName'] == action_name)])

    # Object is already valid, lets add it to the dict
    def add_to_objects_dict(self, obj_count, indago_object_key, requirement, objects_dict):
        '''add_to_objects_dict'''
        # TODO: Get full path, check if full path is already in objectsDict:
        # if it is, use the same id number again; if not, create new id (max id on objectsDict + 1)?
        signal_ID = F'SIGNAL_ID_{obj_count}'

        for obj_item in objects_dict:
            if obj_item['key'] == indago_object_key:
                signal_ID = obj_item['id']
                break

        objects_dict.append({'id': signal_ID,
                             'key': indago_object_key,
                             'objectType': requirement['objectType'],
                             'actionName': requirement['actionName']})

        return objects_dict

    def draw_object(self, object_type):
        # query just need to be done once if needed
        # TODO: When we add more actions.py files, we may see that we need more objectTypes. So just add here
        if object_type in ('signal', 'scope'):
            if not self.full_paths:
                self.full_paths = self.indago_server.full_paths(ct.module_name.contains(""))
            obj = None
            while obj is None:
                rand_num = random.randrange(len(self.full_paths))
                scope = self.indago_server.scope_by_full_path(self.full_paths[rand_num])
                if object_type == 'scope':
                    obj = scope
                else:
                    try:
                        signals = scope.signals()
                        index_rand_num = random.randrange(len(signals))
                        obj = signals[index_rand_num]
                    # Scope can be None and signals can be an empty list
                    except (AttributeError, IndexError, ValueError):
                        continue
            key = obj.full_path
        elif object_type == 'sourceFilePath':
            files = self.indago_server.files()
            rand_num = random.randrange(0, len(files))
            obj = files[rand_num]
            key = obj
        else:
            exit("Used type of object does not exist.")
        return key, obj
