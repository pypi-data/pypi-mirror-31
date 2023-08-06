from setuptools import setup, find_packages


setup(name='x-mroy-1046',
    version='0.1.81',
    description='a anayzer package',
    url='https://github.com/Qingluan/.git',
    author='Qing luan',
    author_email='darkhackdevil@gmail.com',
    license='MIT',
    zip_safe=False,
    packages=find_packages(),
    install_requires=['rsa', 'mroylib-min','fabric3'],
    entry_points={
        'console_scripts': ['x-relay=package.services:main', 'x-control=clients.controll:main', 'x-bak=package.services:main_start_bak']
    },

)
