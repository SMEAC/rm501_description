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

    world_file_name = 'empty.world'
    world_path = os.path.join(get_package_share_directory('rm501_description'), 'worlds', world_file_name)
  
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch'), '/gazebo.launch.py']),
                    launch_arguments={'world': world_path}.items()
             )

    xacro_file = os.path.join(get_package_share_directory('rm501_description'),
                              'urdf',
                              'rm501.urdf.xacro')
    rviz_file = os.path.join(get_package_share_directory('rm501_description'),
                              'rviz',
                              'rm501_display.rviz')                             

    doc = xacro.parse(open(xacro_file))
    xacro.process_doc(doc)
    params = {'robot_description': doc.toxml()}

    position = [0.6, 0.8, 0.11]                   
    orientation = [0.0, 0.0, -0.7]
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'rm501',
                                   '-x', str(position[0]), '-y', str(position[1]), '-z', str(position[2]),
               			   '-R', str(orientation[0]), '-P', str(orientation[1]), '-Y', str(orientation[2]),],
                        output='screen')
                        
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )
    
    rviz_entity = Node(package='rviz2', executable='rviz2',
                        arguments=['-d', rviz_file])
                     
                           
    load_joint_state_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'joint_state_broadcaster'],
        output='screen'
    )

    load_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'joint_state_controller'],
        output='screen'
    )

    return LaunchDescription([
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=spawn_entity,
                on_exit=[load_joint_state_controller],
            )
        ),  
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=load_joint_state_controller,
                on_exit=[load_controller],
            )
        ),        
        gazebo,        
	spawn_entity,
        node_robot_state_publisher,
        rviz_entity,


    ])
