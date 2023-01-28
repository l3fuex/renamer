# General
The program is intendend to rename movie and tv-show files based on a free API which can be found under https://imdb-api.com/.

Before I started this I searched for similar software but could not find anything that satisfied my needs of simplicity and simultaneously is in my budget scope (free). Therefore I decided to do it by myself and made a learning experience out of it with the intention to get deeper into python and git. I am aware that there are similar API implementations available via pip but I wanted to do it by myself - so do not wonder if these are not used in this project.

There where two main design considerations when I wrote this piece of software:  

1. Make as less as possilbe API calls due to the fact that a free account can only do 100 API calls per day.
2. Minimize user interactions to an absolute minimum and try to make automatic descisions whenever possible.

To achieve that the software tries to make precise search requests with as much information as possible with the intention to get exactly one match (advanced search). If this does not result in a match the logic tries to make a broader search (basic search). Doing so the possibility to get more than one match is very likely. To minimize user interactions with basic search the software tries to make the decision based on parsed metadata. If this is not possible and there are still more than one options to choose from than this is the point where the user needs to make a choice. Further, when operating in batch mode (e.g. renaming a whole tv-show season or even several seasons), API responses are being cached to minimize API interactions.

# Prerequirements
+ python3
+ pip3
+ git *(optional)*  

For the software to run python3 has to be installed on your machine. pip3 is needed to install some required python modules. Finally git is needed to actually download the program. Alternatively you can just download the .zip file from github in your browser.

# Installation
> Get an API key from https://imdb-api.com/ by setting up a free account.

## Linux
+ Download  
`git clone https://github.com/l3fuex/renamer.git && cd renamer`
+ Install required python modules  
`pip3 install -r requirements.txt`
+ Insert API key into configuration file  
 `mv config.ini.example config.ini && vi config.ini`  
+ Make program available across the system  
`ln -s /ABSOLUTE/PATH/TO/renamer.py /usr/local/bin/renamer`

## Windows
+ Download  
`git clone https://github.com/l3fuex/renamer.git && cd renamer`
+ Install required python modules  
`pip3 install -r requirements.txt`
+ Insert API key into configuration file  
`move config.ini.example config.ini && config.ini`  
+ Make program available across the system  
`setx PATH %PATH%,C:\PATH\TO\RENAMER\DIR\`

After installation you should be able to call the program from anywhere in your system by typing `renamer` on Linux or `renamer.py` on Windows in a terminal. You should see a general help page about how to use the program. If it does not work make sure the program is in your PATH environment.

# Usage
```
Usage:
    renamer [options] [file]

Options:
    -a, --advanced-search  enable only advanced search mode
    -b, --basic-search     enable only basic search mode
    -h, --help             show this message
    -o, --offset           define offset for episode renaming
    -s, --simulate         no renaming
    -v, --verbose          verbose output

Examples:
    renamer Alien.mkv
    renamer -s Futurama/Season\ {01..03}/*.mkv
    renamer -o -1 futurama_S01E03_somename.mkv
```
