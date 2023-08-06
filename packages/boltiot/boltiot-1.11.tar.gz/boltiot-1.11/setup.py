from distutils.core import setup

setup(
    name = 'boltiot',
    packages = ['boltiot'],
    version = '1.11',
    install_requires=['requests','twilio'],
    description = 'A Python module for communicating with the Bolt Cloud API.', #Add a description here
    author = 'Inventrom Pvt. Ltd.', #Enter an author for the package
    author_email  = 'support@boltiot.com', #Author's Email
    url = 'https://github.com/Inventrom/bolt-api-python', #URL for github repository
    download = 'https://github.com/Inventrom/bolt-api-python/archive/1.12.tar.gz', #Download URL for github repository. Look at instructions...txt file for this part
    keywords = ['iot-platform','bolt','bolt-python'], #Add keywords
    classifiers = [],
)

