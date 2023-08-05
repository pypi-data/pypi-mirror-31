from setuptools import setup, find_packages

setup(
    name='q2k',
    version='1.0.2.a1',
    description='Convert AVR C based QMK keymap and matrix files to YAML Keyplus format',
    url='https://github.com/2Cas/Q2K',
    author='2Cas',
    author_email='reasonstouninstall@tutanota.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development',
        'Topic :: Text Processing',
        'License :: OSI Approved :: MIT License',
    ],
    license='MIT',
    packages=find_packages(include=['q2k', 'q2k.*']),
    python_requires='>=3',
    install_requires=[
        'pyyaml', 'pyparsing', 'termcolor'
    ],
    entry_points = {
        'console_scripts': ['q2k-cli=q2k.core:q2keyplus', 'q2k=q2k.gui:main']  #, 'q2kb=q2k.core:q2kbfirmware']
    },
    keywords = ['keyboard', 'usb', 'hid', 'qmk', 'keyplus'],
    zip_safe=False,
    include_package_data=True,
)
