# redmine_utils/reports

This repository contains a collection of (mainly quarto-) scripts for extracting information from Redmine 
and create various reports.

### How to use this (an alternative that requires you to install [pixi](https://pixi.sh/dev/installation/))

A `pixi` workspace file (*pixi.toml*) is included in the parent directory that (hopefully) provides the various packages dependencies required 
for the included scripts. 

To run scripts in command-line, first do:

        pixi shell

If you want to start your system's rstudio (i.e., not provided by pixi) from within the pixi workspace, do:

        pixi run rstudio

NB! If this does not work directly, you might need to open the file *pixi.toml* in your text editor and change the 
line `rstudio = "/Applications/RStudio.app/Contents/MacOS/RStudio"` to point to the location of your Rstudio installation. 

#### NB! You might also need a conda installation on your system
Some of the quarto-reports use R-reticulate, which apparently will look for a system conda installation. 
This appears to be a known bug with pixi (sigh!). (A plan is to try to switch R-code in quarto docs to python)

## Content

#### `timeLog.qmd`
Extracts logged time for user-defined NBSI experts and period of time and creates a timelog report 
with circle diagrams and tables. Can be run from within rstudio (see above) or with `quarto render`.

#### `timeLogParams.yaml.dist`
Dummy template for the user-created file `timeLogParams.yaml`, with parameters for the `timeLog.qmd` script, 
including a list of users to include tim logs for, the start and end dates of the period to show timelog ofr, 
and a pointer to the config-file with Redmine address and api-key.

#### `createLtsTable.qmd`
Creates the _Table of Peer Review (WABI) projects_ on the 
[Support manager Confluence page](https://scilifelab.atlassian.net/wiki/spaces/NBISSM/pages/2959704083/Table+of+Peer+Review+WABI+projects).
To publish table on Confluence, run from command line `quarto publish confluence createLtsTable.qmd`. 
Currently run monthly by Bengt S.


