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

"""Tests for the sparkler cmd."""
import json
import unittest

import requests_mock

from sparkler import cmd

MOCK_ACTIVITY = json.dumps(
    [{
        "total": 1,
        "week": 1560643200,
        "days": [
            0,
            0,
            1,
            0,
            0,
            0,
            0
        ]
     },
     {
         "total": 7,
         "week": 1561248000,
         "days": [
             1,
             1,
             1,
             1,
             1,
             1,
             1
         ]
     },
     {
         "total": 4,
         "week": 1561852800,
         "days": [
             0,
             1,
             1,
             1,
             1,
             0,
             0
         ]
     }])


class TestSparklerCmd(unittest.TestCase):
    """Test case for all sparkler commands."""

    def test_get_commit_activity(self):
        with requests_mock.Mocker() as m:
            m.register_uri(
                'GET',
                'https://api.github.com/repos/x/y/stats/commit_activity',
                text=MOCK_ACTIVITY)
            data = cmd.get_commit_activity('x/y')
        self.assertListEqual([1, 7, 4], data)
