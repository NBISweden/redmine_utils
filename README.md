# redmine_utils

This repository contains a collection of scripts for communicating with the NBIS Redmine API and extract or change its content.

### How to use this (an alternative that requires you to install [pixi](https://pixi.sh/dev/installation/))

A `pixi` workspace file (*pixi.toml*) is included that (hopefully) provides the various packages dependencies required 
for the included scripts. 

To run scripts in command-line, first do:

        pixi shell

To start rstudio from within the pixi workspace, do:

        pixi run rstudio

NB! If this does not work directly, you might need to open the file *pixi.toml* in your text editor and change the 
line `rstudio = "/Applications/RStudio.app/Contents/MacOS/RStudio"` to point to the location of your rstudio installation. 

## Content

### Report scripts:

#### *timeLog.qmd*
Extracts logged time for user-defined NBSI experts and period of time and creates a timelog report 
with circle diagrams and tables. Typåically trun from within rstudio (see above).

#### *createLtsTable.qmd* 
Creates the _Table of Peer Review (WABI) projects_ on the 
[Support manager Confluence page](https://scilifelab.atlassian.net/wiki/spaces/NBISSM/pages/2959704083/Table+of+Peer+Review+WABI+projects).
To publish table on Confluence, run from command line `quarto publish confluence createLtsTable.qmd`. 
Currently run monthly by Bengt S.

### "Library":

#### *Redmine_apis.py*
Contains the actual functions for communicating with Redmine API -- should always be called from another script. Try to be backwards compatible when editing the functions in this file, or all other scripts will probably break.

#### *config.yaml.dist* 
Dummy template for the user-created file *config.yaml* containing address to the Redmine API 
and user's API-key (available from 'My account'-page in NBIS Redmine)

#### *pixi.toml* 
Provides the `pixi` workspace (see above).

### `scripts/`: 

Dedicated task scripts typically run by Martin D. See [scripts/README.md](scripts/README.md) for more info.

