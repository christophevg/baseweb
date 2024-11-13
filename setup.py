import os
import re
import setuptools

NAME             = "baseweb"
AUTHOR           = "Christophe VG"
AUTHOR_EMAIL     = "contact@christophe.vg"
DESCRIPTION      = "A Pythonic base for building interactive web applications"
LICENSE          = "MIT"
KEYWORDS         = "Flask Vue REST SocketIO"
URL              = "https://github.com/christophevg/" + NAME
README           = ".github/README.md"
CLASSIFIERS      = [
  "Programming Language :: Python :: 3.8",
  "Programming Language :: Python :: 3.9",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Environment :: Web Environment",
  "Intended Audience :: Developers",
  "Topic :: Software Development :: Libraries :: Python Modules",
  "License :: OSI Approved :: MIT License",
  "Development Status :: 4 - Beta",
  
]
INSTALL_REQUIRES = [
  "Flask",
  "Flask-RESTful",
  "Flask-SocketIO",
  "python-dotenv",
  "websocket-client",
  "python-engineio",
  "python-socketio",
  "dotmap",
  "pyfiglet",
  "python-slugify",
  "tabulate",
  
]
ENTRY_POINTS = {
  
}
SCRIPTS = [
  
]

HERE = os.path.dirname(__file__)

def read(file):
  with open(os.path.join(HERE, file), "r") as fh:
    return fh.read()

VERSION = re.search(
  r'__version__ = [\'"]([^\'"]*)[\'"]',
  read(NAME.replace("-", "_") + "/__init__.py")
).group(1)

LONG_DESCRIPTION = read(README)

if __name__ == "__main__":
  setuptools.setup(
    name=NAME,
    version=VERSION,
    packages=setuptools.find_packages(),
    author=AUTHOR,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license=LICENSE,
    keywords=KEYWORDS,
    url=URL,
    classifiers=CLASSIFIERS,
    install_requires=INSTALL_REQUIRES,
    entry_points=ENTRY_POINTS,
    scripts=SCRIPTS,
    include_package_data=True    
  )
