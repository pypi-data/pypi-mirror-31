
# Copyright (c) 2014, 2015
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
from coils.core import NoSuchPathException
from coils.net import PathObject, Protocol

# Can we import the TaskNotifyDemo object?
try:
    from coils.logic.task.services.utility import \
        do_task_notification_preamble, \
        get_name_dictionary_matching_events, \
        send_task_notification_message
    # reference the import to avoid Flake errors
    if (
        do_task_notification_preamble and
        get_name_dictionary_matching_events and
        send_task_notification_message
    ):
        pass
except:
    class TaskNotifyDemo(object):
        pass
else:
    from tasknotify import TaskNotifyDemo

try:
    from coils.logic.task.command import task_matches_rule
    if (
        task_matches_rule
    ):
        pass
except:
    class TaskRuleDemo(object):
        pass
else:
    from taskrule import TaskRuleDemo

OGO_INDEX_OF_TOOLS = {
    'tasknotifydemo': TaskNotifyDemo,
    'taskruledemo': TaskRuleDemo,
}


class ToolboxRoot(PathObject, Protocol):
    __pattern__ = 'toolbox'
    __namespace__ = None
    __xmlrpc__ = False

    def __init__(self, parent, **params):
        PathObject.__init__(self, parent, **params)

    @property
    def name(self):
        return 'toolbox'

    def is_public(self):
        return False

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if name in OGO_INDEX_OF_TOOLS:
            return OGO_INDEX_OF_TOOLS[name](
                self, name,
                context=self.context,
                request=self.request,
                parameters=self.parameters,
            )
        else:
            raise NoSuchPathException(name)

    def do_GET(self):
        self.request.simple_response(200, data=self.context.cluster_id, )
