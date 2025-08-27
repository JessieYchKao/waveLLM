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

'''Action DriverTracing'''

from actionslib.base_actions import *
from actionslib.lib import print_progress

class ActionDriverTracing(BaseAction):
    ##### actions.py object requirements
    def driver_tracing_constraint(self, indago_object):
        return bool(indago_object.drivers())

    # This method tries to determine if input signals intersect on one or more bits
    @staticmethod
    def is_signal_intersection(signal_1, signal_2):
        if signal_1.path != signal_2.path:
            return False
        return signal_1.base_name == signal_2.base_name

	##### Perform Actions (this is specific for each all actions.py)
    def current_action(self):
        main_win = self.indago_server.gui_components(ct.name=='main_win')[0]
        full_paths = self.get_keys_from_objects_dict("signal", "driverTracing")
        dbs = self.indago_server.server_info.values_databases
        end_time = dbs[0].end
        for i, full_path in enumerate(full_paths):
            signal = self.indago_server.signal_by_full_path(full_path)
            self.indago_server.set_time(end_time)
            if signal is None:
                print(f"Signal not found: {full_path}")
                continue
            result = main_win.trace_cause(signal)
            if result.status == False:
                print(f' ERROR trace cause failed at index {i}: {result.details} signal: {signal.full_path}')
            print_progress('Processed', i)


action = ActionDriverTracing('This file is focused on measuring performance on doing driver tracing.')
action.add_required_object('driverTracing', 'signal', action.test_count, action.no_constraint)
action.execute_action()
