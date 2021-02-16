# new-softserve
The development of the Jackbord-python library starts here

## Crash course documentation document available here: https://docs.google.com/document/d/1fniUAaZcdtHJZzuqJWjoJGyMrFEbRqHns_oaT8hcBl4/edit?usp=sharing
I haven't yet done "proper" documentation yet plz don't hurt me

Ideally, you've visited this repository because you know what this is and are helping out with developing/testing this library.

If not, welcome! Sorry if this is a rather poorly organized github repository. I'm kind of new to github and will eventually implement things such as "best practices" and whatnot.
In the meantime, this isn't ready for you yet. You deserve better, like when this has been all tidied up and made to be as professional as possible.

### What softserve is:
Softserve is a companion python library for the Jackbord. It allows you to use variables emitted from the jackbord and the ability to send commands to the jackbord all from the comfort of your python script.

I will eventually get around to making a proper documentation manual describing exactly what you can do with this and how to do it.

#### Distributions: 
Softserve comes in both of the distributions. Standalone and pip. This may seem a bit bootleg right now but eventually it will be set up like all of the good repos on github.


#### Pip:
This distribution is the whl file that's in the root of this. I'm assuming you know that pip is python's package manager, and can install the library with
`pip install softserve-xx.x.x-py3-none-any` (The x's are just version specific numbers. Don't be afraid to use autocomplete) Be carful that you pip install from the .whl file, because someone else also came up with the name softserve and it's a library that already exists in the pip repository. I might change my library's name when I come up with a better one.

#### Standalone:
The standalone version is designed for the student who is using their school's computer and don't have access to a console or the ability to install pip, etc.
If this is you, you really just need to download the softserve-standalone.zip file. You can extract it into the same folder as your python program, or dump into a convinient location and add the following lines to the beginning of your python program to temporarily add it to python's path:
```python
import sys
sys.path.append("path/to/folder/containing/the/softserve/folder")
```

##### Examples:
Both distributions come with a few example files I coded up. These require access to a jackbord with a potentiometer and some rgb led strips.
The examples in the standalone distribution are already edited like I mentioned above so you can just run them with python and *should* work okay.
Otherwise, you can run the example programs in the example folder in the root of this repository

More documentation and general polishing and professionalism coming soon...
