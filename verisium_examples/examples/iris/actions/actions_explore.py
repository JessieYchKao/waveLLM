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

'''Action Explore'''

from actionslib.base_actions import *
from actionslib.lib import print_progress

class ActionExplore(BaseAction):
    ##### actions.py object requirements
    def explore_constraint(self, indago_object):
        exploration = self.indago_server.gui_components(ct.name == "EXPLORATION")[0]
        return exploration.explore(indago_object.full_path).status

	##### Perform Actions (this is specific for each all actions.py)
    def current_action(self):
        full_paths = self.get_keys_from_objects_dict("signal", "explore")
        exploration = self.indago_server.gui_components(ct.name == "EXPLORATION")[0]
        for i, full_path in enumerate(full_paths):
            signal = self.indago_server.signal_by_full_path(full_path)
            if signal is None:
                print(f"Signal not found: {full_path}")
                continue
            exploration.explore(signal)
            print_progress('Processed Explore Drivers', i)

        for i, full_path in enumerate(full_paths):
            signal = self.indago_server.signal_by_full_path(full_path)
            if signal is None:
                print(f"Signal not found: {full_path}")
                continue
            exploration.explore(signal, explore_type=ExploreType.LOADS)
            print_progress('Processed Explore Loads', i)

        for i, full_path in enumerate(full_paths):
            signal = self.indago_server.signal_by_full_path(full_path)
            if signal is None:
                print(f"Signal not found: {full_path}")
                continue
            exploration.explore(signal, explore_type=ExploreType.CONNECTIVITY)
            print_progress('Processed Explore Connectivity', i)


action = ActionExplore('This file is focused on measuring performance when calling the explore API.')
action.add_required_object('explore', 'signal', action.test_count, action.no_constraint)
action.execute_action()
