from setuptools import find_packages, setup

package_name = 'turtlebot_vision'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),(
        'share/turtlebot_vision/launch',
        ['launch/agv_launch.py'],
    ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='learn',
    maintainer_email='learn@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
    'console_scripts': [
        'camera_view = turtlebot_vision.camera_view:main',
        'blue_test = turtlebot_vision.blue_test:main',
    ],
},
)
