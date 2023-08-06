from setuptools import find_packages, setup


setup(
    name="regulations",
    version="8.4.2",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'cached-property',
        'django>=1.8,<1.12',
        'enum34;python_version<"3.4"',
        'futures;python_version<"3"',
        'requests',
        'six',
    ],
    extras_require={
        'notice_comment': ['boto3', 'celery', 'requests-toolbelt'],
    },
    classifiers=[
        'License :: Public Domain',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication'
    ]
)
