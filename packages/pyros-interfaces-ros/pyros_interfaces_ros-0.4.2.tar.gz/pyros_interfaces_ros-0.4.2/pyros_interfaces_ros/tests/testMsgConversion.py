from __future__ import absolute_import, division, print_function

import os
import sys
import pickle

# This is needed if running this test directly (without using nose loader)
if __name__ == '__main__':
    # prepending because ROS relies on package dirs list in PYTHONPATH and not isolated virtualenvs
    # And we need our current module to be found first, before any similar package from another workspace
    current_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    # if not current_path in sys.path:
    sys.path.insert(1, current_path)  # sys.path[0] is always current path as per python spec


# Unit test import
from pyros_interfaces_ros import message_conversion as msgconv

# ROS imports should now work from ROS or from python ( even without ROS env setup)
import rospy

# useful test tools
import nose
import pytest

# Test all standard message
import std_msgs.msg as std_msgs


# TODO : change this customJSON -> ROS conversion by JSON -ujson-> py -rospy-> ROS
# TODO : achieve SYMMETRY : what we put in == what we get out ( no "data" field added )
def test_String_default():
    msg = std_msgs.String()
    val = msgconv.extract_values(msg)
    assert val["data"] == str()  # "data" : should not appear here


def test_String_custom():
    msg = std_msgs.String("teststr")
    msgconv.populate_instance({"data": "teststr2"}, msg)  # we shouldnt need "data" here
    val = msgconv.extract_values(msg)
    assert val["data"] == "teststr2"


def test_msg_exception_pickle():
    exc = msgconv.NonexistentFieldException("message type", ["field1", "field2"])

    pbuf = pickle.dumps(exc)
    pexc = pickle.loads(pbuf)

    assert pexc.basetype == "message type"
    assert len(pexc.fields) == 2
    assert "field1" in pexc.fields
    assert "field2" in pexc.fields

# TODO : assert both "string" and "std_msgs/String" are convertible from&to "str" and "unicode"


#TODO : assert exception are being thrown


# if __name__ == '__main__':
#     # finally running nose
#     nose.runmodule()

if __name__ == '__main__':
    pytest.main(['-s', __file__])

