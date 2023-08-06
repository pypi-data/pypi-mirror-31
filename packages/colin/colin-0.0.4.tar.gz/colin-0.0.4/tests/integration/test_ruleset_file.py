# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import json
import tempfile
import colin
import random

def get_results_from_colin_labels_image(ruleset_name=None, ruleset_file=None):
    return colin.run("colin-labels", ruleset_name=ruleset_name, ruleset_file=ruleset_file)


def test_colin_labels_image():
    assert get_results_from_colin_labels_image()


def generate_json_file(colin_json):
    with tempfile.NamedTemporaryFile(dir='/tmp', delete=True) as tmpfile:
        temp_file_name = tmpfile.name

    with open(temp_file_name, 'w') as outfile:
        json.dump(colin_json, outfile, ensure_ascii=True)
    return temp_file_name


def test_specific_ruleset():
    colin_json={"labels": {
        "required": [
            "maintainer",
            "name",
            "com_redhat_component"
        ],
        "optional": [
            "help"
        ]
      },
    }


    with open(generate_json_file(colin_json), "r") as f:
        result = get_results_from_colin_labels_image(ruleset_file=f)
    assert result
    expected_dict = {"maintainer_label_required": "PASS",
                     "name_label_required": "PASS",
                     "com_redhat_component_label_required": "PASS",
                     "help_label": "WARN",
    }
    labels_dict = {}
    for res in result.all_results:
        labels_dict[res.check_name] = res.status
    for key in expected_dict.keys():
        assert labels_dict[key] == expected_dict[key]
