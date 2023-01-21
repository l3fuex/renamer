# General
The program is intendend to rename movie and tv-show files based on a free API which can be found under https://imdb-api.com/.

Before I started this I searched for similar software but could not find anything that satisfied my needs of simplicity and simultaneously is in my budget scope of open source software. Therefore I decided to do it by myself "how hard can it be??" and make a learning experience out of it with the intention to get deeper into python and git. I am aware that there are similar API implementations available via pip. But I wanted to do it by myself - so do not wonder if these are not used in this project.

One design consideration was to make as less as possible API calls but also keep user interatcions at an absolute minimum. To achieve that the software tries to make precise search requests with as much information as possible with the intention to get exactly one match (advanced search). If this does not result in a match the logic tries to make a broader search (basic search). Doing so the possibility to get more than one match is very likely. To minimize user interactions with basic search the software tries to make the decision based on parsed metadata. If this is not possible and there are still more than one options to choose from the user needs to make a choice. Also for batch renaming of whole tv-shows API responses are cached to minimize API interations.

# Installation
## Linux
1. `git clone git@github.com:l3fuex/renamer.git`
2. `cd renamer`
3. `pip3 install -r requirements.txt`
4. `mv config.ini.example config.ini`
5. Get yourself an API key from https://imdb-api.com/ by registering an account and instert the key in the config.ini file
```
[IMDB]
language: EN
apikey: <insert_api_key_here>
```
6. `ln -s /absolute/path/to/renamer.py /usr/local/bin/renamer`

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
