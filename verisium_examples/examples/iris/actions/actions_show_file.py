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

'''Action Show File'''

from actionslib.base_actions import *
from actionslib.lib import print_progress

class ActionShowFile(BaseAction):
    ##### Perform Actions (this is specific for each all actions.py)
    def current_action(self):
        source_browser = self.indago_server.gui_components(ct.type == ComponentType.SOURCE)[0]
        files = self.get_keys_from_objects_dict('sourceFilePath', 'showFile')
        for i, file in enumerate(files):
            source_browser.show_file(file)
            print_progress('Processed', i)


action = ActionShowFile('This file is focused on measuring performance when opening files in the source viewer.')
action.add_required_object('showFile', 'sourceFilePath', action.test_count, action.no_constraint)
action.execute_action()
