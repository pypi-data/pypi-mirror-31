from setuptools import setup, find_packages


setup(name='LoreleiClient',
    version='0.1.5.3',
    description='The text based MUD made by Lorinthio',
    author='Lorinthio',
    author_email='benrandallswg@gmail.com',
    packages=find_packages(),
    install_requires=[
        'twisted',
        'pygame',
        'enum34',
        'LoreleiLib'
    ],
    include_package_data = True,
    package_data = {
    '' : ['*.png'],
    },
    zip_safe=False)