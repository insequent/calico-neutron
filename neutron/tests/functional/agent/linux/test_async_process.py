# Copyright 2013 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import eventlet
import fixtures

from six import moves

from neutron.agent.linux import async_process
from neutron.agent.linux import utils
from neutron.tests import base


class TestAsyncProcess(base.BaseTestCase):

    def setUp(self):
        super(TestAsyncProcess, self).setUp()
        self.test_file_path = self.useFixture(
            fixtures.TempDir()).join("test_async_process.tmp")
        self.data = [str(x) for x in moves.xrange(4)]
        with file(self.test_file_path, 'w') as f:
            f.writelines('%s\n' % item for item in self.data)

    def _check_stdout(self, proc):
        # Ensure that all the output from the file is read
        output = []
        while output != self.data:
            new_output = list(proc.iter_stdout())
            if new_output:
                output += new_output
            eventlet.sleep(0.01)

    def test_stopping_async_process_lifecycle(self):
        proc = async_process.AsyncProcess(['tail', '-f',
                                           self.test_file_path])
        proc.start()
        self._check_stdout(proc)
        proc.stop()

        # Ensure that the process and greenthreads have stopped
        proc._process.wait()
        self.assertEqual(proc._process.returncode, -9)
        for watcher in proc._watchers:
            watcher.wait()

    def test_async_process_respawns(self):
        proc = async_process.AsyncProcess(['tail', '-f',
                                           self.test_file_path],
                                          respawn_interval=0)
        proc.start()

        # Ensure that the same output is read twice
        self._check_stdout(proc)
        pid = utils.get_root_helper_child_pid(proc._process.pid,
                                              proc.root_helper)
        proc._kill_process(pid)
        self._check_stdout(proc)
        proc.stop()
