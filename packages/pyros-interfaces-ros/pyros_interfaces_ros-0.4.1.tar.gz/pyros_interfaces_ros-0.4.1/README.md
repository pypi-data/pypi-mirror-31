# pyros-rosinterface
ROS Interface sub-package for Pyros


Assumptions
--------------

- OS is Ubuntu Trusty
- ROS is already known. If not, get informations and tutorials on http://ros.org

ROS Indigo System Setup
-----------------------
- Install useful python packages if you don't already have them :
```bash
$ sudo apt-get install virtualenvwrapper
```
- Install ROS Indigo : http://wiki.ros.org/indigo/Installation/Ubuntu
TL;DR : 
```bash
$ sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
$ sudo apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net:80 --recv-key 421C365BD9FF1F717815A3895523BAEEB01FA116
$ sudo apt-get update
$ sudo apt-get install ros-indigo-desktop
$ sudo rosdep init
```


ROS Talker Launch
-----------------
Run the ROS talker and listener nodes as usual using roslaunch, in a separate terminal : 

```
$ source /opt/ros/indigo/setup.bash 
$ roslaunch roscpp_tutorials talker_listener.launch 
```

Now you can run the pyros ROS interface node :
- from ROS itself (using the launcher provided),
- **OR** from a separate python virtual environment, that will access your ROS environment via pyros-setup.

Launching on ROS
----------------

**_TODO_**



Running from python
-------------------

```
$ mkvirtualenv pyros-ros --system-site-packages
$ workon pyros-ros
(pyros-ros) $ pip install pyros_interfaces_ros
[...]
$ python -m pyros_interfaces_ros --sub ".*"
Re-adding /opt/ros/jade/lib/python2.7/dist-packages in front of sys.path
[pyros] Node started as [None <= ipc:///tmp/zmp-pyros-jRbGSV/services.pipe]
[INFO] [WallTime: 1493198579.422698] RosInterface pyros node started with args : []
[INFO] [WallTime: 1493198579.426763] [pyros_interfaces_ros.ros_interface] ROS Interface initialized with:
        -    services : []
        -    publishers : []
        -    subscribers : 
        - .*
        -    params : []
        -    enable_cache : False
        
[INFO] [WallTime: 1493198580.437716] /pyros Pyros.ros : Adding publisher interface /chatter <class 'std_msgs.msg._String.String'>
[INFO] [WallTime: 1493198580.843025] /pyros Pyros.ros : Adding publisher interface /rosout <class 'rosgraph_msgs.msg._Log.Log'>

```

_**TODO : using dynamic_reconfigure you can dynamically adjust what is exposed or not, without restarting the node.**_

From this point on, you will need the [Pyros](https://github.com/asmodehn/pyros.git) framework installed to be able to interract with the ROS system using the pyros client.