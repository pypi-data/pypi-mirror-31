Infinite_image_downloader
=====
_Developer: Zhiao Zhou ([@zhiaozhou](https://github.com/zhiaozhou) | <zz1749@nyu.edu> | [Linkedin](https://www.linkedin.com/in/zhiaozhou/))_ 

Infinite_image-downloader is a python library for automatically downloading requested number of images from Google image search by one keyword.

The principle is that since Google has limited the number of outputs per keyword(1000 maximum), after getting numbers of pictures and their urls of the first search, the downloader is going to search more images using the urls that were just achieved and then recursively go on.

Dependencies
=============
pgmpy has following non optional dependencies:
- Python 2.7 or Python 3
- request 
- selenium 
- socket
- Geckodriver for Firefox users

Installation
=============
Using pip:
```
$ pip install infinite_image_downloader
```

Or for installing the latest codebase:
```
$ git clone https://github.com/zhiaozhou/infinite_image_downloader.git
$ cd infinite_image_downloader/
$ python setup.py install
```

Documentation and usage
=======================

Now this package can be only used with a Firefox browser installed.

Then you will have to install Geckodriver from [Geckodriver/releases](https://github.com/mozilla/geckodriver/releases) and then put the executable file inside the root folder of your Firefox directory (Ex. C:\Program Files\Mozilla Firefox\)

For Mac users, put it under usr/local/bin

Then after installing the package using pip
you can start to use it by typing infinite_image_downloader [keyword] [numbers of images you want] [download path](optional)

An example is shown below

![example](example.gif)

License
=======
infinite_image_downloader is released under MIT License.