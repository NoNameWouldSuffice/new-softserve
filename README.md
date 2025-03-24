##Project is now archived. I have been away from this project for years and have no intention to continue developing it.

## new-softserve

### Crash course documentation document available here: https://docs.google.com/document/d/1fniUAaZcdtHJZzuqJWjoJGyMrFEbRqHns_oaT8hcBl4/edit?usp=sharing


### What softserve is:
Softserve is a companion python library for the Jackbord. It allows you to use variables emitted from the jackbord and the ability to send commands to the jackbord all from the comfort of your python script.

I will eventually get around to making a proper documentation manual describing exactly what you can do with this and how to do it.

#### Distributions: 
Softserve comes in both of the distributions. Standalone and pip. This may seem a bit bootleg right now but eventually it will be set up like all of the good repos on github.


#### Pip:
This distribution is the whl file you can download from the latest release. I'm assuming you know that pip is python's package manager, and can install the library with
`pip install softserve-xx.x.x-py3-none-any` (The x's are just version specific numbers. Don't be afraid to use autocomplete) Be carful that if you pip install from the .whl file, because someone else also came up with the name softserve and it's a library that already exists in the pip repository. I might change my library's name when I come up with a better one.

#### Standalone:
The standalone version is designed for the student who is using their school's computers and don't have access to a console or the ability to install pip, etc.
If this is you, you really just need to download the softserve-standalone.zip file from the latest release. You can extract it into the same folder as your python program, or dump into a convinient location and add the following lines to the beginning of your python program to temporarily add it to python's path:
```python
import sys
sys.path.append("path/to/folder/containing/the/softserve/folder")
```

##### Examples:
Both distributions come with a few example files I coded up. These require access to a jackbord with a potentiometer and some rgb led strips.
The examples in the standalone distribution are already edited like I mentioned above so you can just run them with python and *should* work okay.
Otherwise, you can run the example programs in the example folder in the root of this repository
