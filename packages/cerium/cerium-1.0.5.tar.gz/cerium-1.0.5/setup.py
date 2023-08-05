# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.


from setuptools import setup
'''
python setup.py sdist
python setup.py bdist_wheel
twine upload dist/*
pip install dist\cerium-1.0.4.tar.gz
'''

setup(
    name='cerium',
    packages=['cerium'],
    version='1.0.5',
    license='Apache 2.0',
    author='White Turing',
    author_email='fujiawei@stu.hznu.edu.cn',
    description='A Android automation framework.',
    long_description='This project is mainly targeted to users that need to communicate with Android devices in an automated fashion, such as in automated testing.',
    url='https://github.com/fjwCode/cerium',
    keywords=['android', 'adb', 'automation'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries',
    ],
    data_files=[('Lib/site-packages/adb', ['adb/adb.exe',
                                           'adb/AdbWinApi.dll', 'adb/AdbWinUsbApi.dll'])],
)
