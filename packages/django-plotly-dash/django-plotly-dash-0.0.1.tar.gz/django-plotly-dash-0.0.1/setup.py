#!/usr/bin/env python

from setuptools import setup

import django_plotly_dash as dpd

VERSION = dpd.__version__

setup(
    name="django-plotly-dash",
    version=VERSION,
    url="https://github.com/GibbsConsulting/django-plotly-dash",
    description="Django use of plotly dash apps through template tags",
    author="Mark Gibbs",
    author_email="django_plotly_dash@gibbsconsulting.ca",
    license='MIT',
    packages=[
    'django_plotly_dash',
    ],
    classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    ],
    keywords='django plotly plotly-dash dash dashboard',
    project_urls = {
    'Source': "https://github.com/GibbsConsulting/django-plotly-dash",
    'Tracker': "https://github.com/GibbsConsulting/django-plotly-dash/issues",
    },
    install_requires = ['plotly',
                        'dash',
                        'dash-core-components',
                        'dash-html-components',
                        'dash-renderer',
                        'Django',],
    python_requires=">=3",
    
    )

