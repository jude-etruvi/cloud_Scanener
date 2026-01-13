"""
Setup script for Cloud Security Scanner
"""

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='cloud-security-scanner',
    version='1.0.0',
    description='Multi-cloud security scanning platform using Prowler and cloudscan',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Cloud Security Team',
    python_requires='>=3.8',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'cloud-scanner=scanner:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'Topic :: Security',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
