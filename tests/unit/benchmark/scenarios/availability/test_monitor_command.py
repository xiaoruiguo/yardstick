#!/usr/bin/env python

##############################################################################
# Copyright (c) 2015 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

# Unittest for
# yardstick.benchmark.scenarios.availability.monitor.monitor_command

from __future__ import absolute_import
import mock
import unittest

from yardstick.benchmark.scenarios.availability.monitor import monitor_command


@mock.patch('subprocess.check_output')
class ExecuteShellTestCase(unittest.TestCase):

    def test__fun_execute_shell_command_successful(self, mock_subprocess_check_output):
        cmd = "env"
        mock_subprocess_check_output.return_value = (0, 'unittest')
        exitcode, _ = monitor_command._execute_shell_command(cmd)
        self.assertEqual(exitcode, 0)

    @mock.patch('yardstick.benchmark.scenarios.availability.monitor.monitor_command.LOG')
    def test__fun_execute_shell_command_fail_cmd_exception(self, mock_log,
                                                           mock_subprocess_check_output):
        cmd = "env"
        mock_subprocess_check_output.side_effect = RuntimeError
        exitcode, _ = monitor_command._execute_shell_command(cmd)
        self.assertEqual(exitcode, -1)
        mock_log.error.assert_called_once()


@mock.patch('subprocess.check_output')
class MonitorOpenstackCmdTestCase(unittest.TestCase):

    def setUp(self):
        host = {
            "ip": "10.20.0.5",
            "user": "root",
            "key_filename": "/root/.ssh/id_rsa"
        }
        self.context = {"node1": host}
        self.config = {
            'monitor_type': 'openstack-api',
            'command_name': 'nova image-list',
            'monitor_time': 1,
            'sla': {'max_outage_time': 5}
        }

    def test__monitor_command_monitor_func_successful(self, mock_subprocess_check_output):

        instance = monitor_command.MonitorOpenstackCmd(self.config, None, {"nova-api": 10})
        instance.setup()
        mock_subprocess_check_output.return_value = (0, 'unittest')
        ret = instance.monitor_func()
        self.assertTrue(ret)
        instance._result = {"outage_time": 0}
        instance.verify_SLA()

    @mock.patch('yardstick.benchmark.scenarios.availability.monitor.monitor_command.LOG')
    def test__monitor_command_monitor_func_failure(self, mock_log, mock_subprocess_check_output):
        mock_subprocess_check_output.return_value = (1, 'unittest')
        instance = monitor_command.MonitorOpenstackCmd(self.config, None, {"nova-api": 10})
        instance.setup()
        mock_subprocess_check_output.side_effect = RuntimeError
        ret = instance.monitor_func()
        self.assertFalse(ret)
        mock_log.error.assert_called_once()
        instance._result = {"outage_time": 10}
        instance.verify_SLA()

    @mock.patch(
        'yardstick.benchmark.scenarios.availability.monitor.monitor_command'
        '.ssh')
    def test__monitor_command_ssh_monitor_successful(self, mock_ssh, mock_subprocess_check_output):

        mock_subprocess_check_output.return_value = (0, 'unittest')
        self.config["host"] = "node1"
        instance = monitor_command.MonitorOpenstackCmd(
            self.config, self.context, {"nova-api": 10})
        instance.setup()
        mock_ssh.SSH.from_node().execute.return_value = (0, "0", '')
        ret = instance.monitor_func()
        self.assertTrue(ret)
