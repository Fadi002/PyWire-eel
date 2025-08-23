from setuptools import setup, find_packages

setup(
    name='pywire-eel',
    version='0.1.0',
    description='PyWire is a lightweight Python library that allows you to create simple desktop GUI applications using HTML, CSS, and JavaScript, while giving full access to Python’s functionality and libraries.',
    author='Fadi002',
    url='https://github.com/Fadi002/pywire-eel',
    packages=find_packages(),
    package_data={
        'pywire': [
            'web/*',
        ]
    },
    install_requires=[],
    python_requires='>=3.7',
    include_package_data=True,
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
