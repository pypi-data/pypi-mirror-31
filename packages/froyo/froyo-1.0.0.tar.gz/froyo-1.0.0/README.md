# froyo

a simple command line tool to build your website

it minifies your files, compresses images and processes server-side includes

## usage

`>> froyo path/to/src/folder [path/to/dest/folder] [--watch]`

### arguments

postional

`source` - path to source folder
`dest` - path to destination folder, if blank it will default to `[source\]_dist` and it will be created if it does not exist

optional

`--watch` - will watch the source for changes

### installation

#### PyPi

`pip install froyo`

#### GitHub

clone from github
`>> git clone https://github.com/kartikye/froyo.git`

navigate to the directory
`>> cd froyo`

run the install command
`>> python setup.py install`