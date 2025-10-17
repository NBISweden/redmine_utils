# redmine_utils

This repository contains a collection of scripts for communicating with the NBIS Redmine API and extract or change its content.

### How to use this (an alternative that requires you to install [pixi](https://pixi.sh/dev/installation/))

A `pixi` workspace file (*pixi.toml*) is included that (hopefully) provides the various packages dependencies required 
for the included scripts (both Python and Quarto). 

To run scripts in command-line, first do:

        pixi shell

To start Rstudio from within the pixi workspace, do:

        pixi run rstudio

NB! If you are not on MacOSX or this does not work directly, you might need to open the file *pixi.toml* in your text 
editor and change the line `rstudio = "/Applications/RStudio.app/Contents/MacOS/RStudio"` to point to the location of 
your rstudio installation. 

## Content

### `config.yaml.dist`
Dummy template for the user-created file *config.yaml* containing address to the Redmine API 
and user's API-key (available from 'My account'-page in NBIS Redmine)

### `pixi.toml` 
Provides the `pixi` workspace (see above).


### `reports/`

Scripts for creating various reports based on info extracted from Redmine. 
See [reports/README.md](reports/README.md) for more info.

### `scripts/`

Dedicated task scripts typically run by Martin D. See [scripts/README.md](scripts/README.md) for more info.

### `lib/`

Contains the actual functions for communicating with Redmine API. See [lib/README.md](lib/README.md) for more info.

