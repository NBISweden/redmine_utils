# redmine_utils

This repository contains a collection of scripts for communicating with the NBIS Redmine API and extract or change its content.

### How to use this (an alternative that requires you to install [pixi](https://pixi.sh/dev/installation/))

A `pixi` workspace file (*pixi.toml*) is included that (hopefully) provides the various packages dependencies required 
for the included scripts (both Python and Quarto). 

To run scripts in command-line, first do:

        pixi shell

All dependencies will be automatically installed the first time you run `pixi shell` 

#### Time log report

First you need to fill in the correct information in the 2 config files `config.yaml`, and `timeLogParams.yaml`, see info below in *Contents* section.
Then you can either first run `pixi shell` and then render the report with:

     	 cd reports
	 pixi shell
	 quarto render timeLog.qmd

An alternative is to run all of it in one go without activating pixi first.

   	 cd reports      
   	 pixi run quarto render timeLog.qmd      

#### createLtsTable

Not yet implemented in python, please use the branch with R based code. 


#### Development

*OBS!* If you want to edit the code and do development you may use e.g. Rstudio or VSCode. You might need to open the file *pixi.toml* in your text 
editor and change the line `rstudio = "/Applications/RStudio.app/Contents/MacOS/RStudio"` to point to the location of 
your rstudio installation. 

#### NB! You might also need a conda installation on your system

## Content

### `config.yaml.dist`
Dummy template for the user-created file `config.yaml containing address to the Redmine API 
and user's API-key (available from 'My account'-page in NBIS Redmine)

### `reports/timeLogParams.yaml.dist`
Dummy template for the user-created file `timeLogParams.yaml`, where you define staff names and time period for the report.

### `pixi.toml` 
Provides the `pixi` workspace (see above).

### `reports/`

Scripts for creating various reports based on info extracted from Redmine. 
See [reports/README.md](reports/README.md) for more info.

### `scripts/`

Dedicated task scripts typically run by Martin D. See [scripts/README.md](scripts/README.md) for more info.

### `lib/`

Contains the actual functions for communicating with Redmine API. See [lib/README.md](lib/README.md) for more info.

