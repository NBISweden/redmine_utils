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
Contains the actual functions for communicating with Redmine API -- should always be called from another script.

#### *config.yaml.dist* 
Dummy template for the user-created file *config.yaml* containing address to the Redmine API 
and user's API-key (available from 'My account'-page in NBIS Redmine)

#### *pixi.toml* 
Provides the `pixi` workspace (see above).

### Dedicated task scripts. Typically run by Martin D, don't use and don't edit:

#### *script_send_out_user_survey_to_closed_projects.py* 
Will send an email to the `pi_email` of all projects that 
have been either closed or resolved in the specifed date range. Will only send to projects that have the 
checkbox `send_user_survey` checked. After the email is sent, the checkbox will be unchecked to avoid sending 
multiple emails, as well as updating the project description to indicate that the survey has been sent.
```bash
python3 script_send_out_user_survey_to_closed_projects.py -c config.yaml -s 2025-03-04 -e 2025-10-12
```

###### Last run

To keep track of start and end points.
```bash
python3 script_send_out_user_survey_to_closed_projects.py -c config.yaml -s 2025-03-04 -e 2025-10-12
```

#### Other scripts
- *script_bengt_vr_lifespan_stats.py* 
- *script_copy_values_between_fields.py*
- *script_resolve_old_lts_issues.py*

---

#### TODO

* For next time (spring 2026), only look for resolved issues.
  * Or maybe we should include closed then as well? The `send_survey_when_closed` checkbox will be unticked for the ones we sent to now, and people might make mistakes and close an issue directly without passing through resolved first.
* Refactor the script to be stuctured more in functions to keep `main` lean.
* Use a fuction user with the proper permissions to interact with redmine.

