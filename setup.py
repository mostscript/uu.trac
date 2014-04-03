from setuptools import setup, find_packages

version = '0.9.dev0'

setup(
    name='uu.trac',
    version=version,
    description='Plone add-on for trac ticket listing.',
    long_description=(
        open("README.txt").read() + "\n" +
        open("CHANGES.txt").read()
        ),
    classifiers=[
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Framework :: Plone",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
    keywords='',
    author='Sean Upton',
    author_email='sean.upton@hsc.utah.edu',
    url='http://github.com/upiq',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['uu'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zope.schema>=3.8.0',
        'plone.app.dexterity',
        'plone.uuid',
        'Products.CMFPlone>=4.3',
        # -*- Extra requirements: -*-
    ],
    extras_require = {
        'test': ['plone.app.testing>=4.0'],
    },
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
    )

