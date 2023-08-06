from setuptools import setup, find_packages


setup(
    name='django-profanity-filter',
    version='0.2.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'inflection',
    ],
    package_data={'profanity': ['wordlist.txt']},
    url='https://github.com/ReconCubed/django-profanity-filter',
    license='BSD 3-clause "New" or "Revised License"',
    author='recon',
    author_email='recongamingsam@gmail.com',
    download_url='https://github.com/ReconCubed/django-profanity-filter/archive/0.2.tar.gz',
    description='Django Profanity Filter is a simple Django app that introduces a range of template tags and filters and model validators that remove or censor inappropriate language.',
    classifiers=[
                  'Environment :: Web Environment',
                  'Framework :: Django',
                  'Framework :: Django :: 2.0',
                  'Intended Audience :: Developers',
                  'License :: OSI Approved :: BSD License',
                  'Operating System :: OS Independent',
                  'Programming Language :: Python',
                  'Programming Language :: Python :: 3.5',
                  'Programming Language :: Python :: 3.6',
                  'Programming Language :: Python :: 3.7',
                  'Topic :: Internet :: WWW/HTTP',
                  'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
              ],

)
