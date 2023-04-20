import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument, IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node

import xacro


def generate_launch_description():

    xacro_file = os.path.join(get_package_share_directory('rm501_description'),
                              'urdf',
                              'rm501.urdf.xacro')
    rviz_file = os.path.join(get_package_share_directory('rm501_description'),
                              'rviz',
                              'rm501_display.rviz')                             

    doc = xacro.parse(open(xacro_file))
    xacro.process_doc(doc)
    params = {'robot_description': doc.toxml()}




    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )
    
    node_robot_joint_publisher = Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            output='screen',
            parameters=[params]
    )



    rviz_entity = Node(package='rviz2', executable='rviz2',
                        arguments=['-d', rviz_file])
                     
    return LaunchDescription([
        node_robot_state_publisher,
        node_robot_joint_publisher,
        rviz_entity,
    ])
