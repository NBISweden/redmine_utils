# redmine_utils

This repository contains various scripts for communicating with the NBIS Redmine API and extract or change its content.

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

- *timeLog.qmd* extracts logged time for user-defined NBSI experts and period of time and creates a timelog report 
with circle diagrams and tables.

- *createLtsTable.qmd* creates the _Table of Peer Review (WABI) projects_ on the 
[Support manager Confluence page](https://scilifelab.atlassian.net/wiki/spaces/NBISSM/pages/2959704083/Table+of+Peer+Review+WABI+projects).
To publish table on Confluence, run from command line `quarto publish confluence createLtsTable.qmd`. 
Currently run monthly by Bengt S.

### "Library":

- *Redmine_apis.py* contains the actual functions for communicating with Redmine API -- should always be called 
from another script.

- *config.yaml.dist* Dummy template for the user-created file *config.yaml* containing address to the Redmine API 
and user's API-key (available from 'My account'-page in NBIS Redmine)

- *pixi.toml* provides 

### Dedicated task scripts. Typically run by Martin D, don't use and don't edit:

- *script_send_out_user_survey_to_closed_projects.py* sends out user survey
- *script_bengt_vr_lifespan_stats.py* 
- *script_copy_values_between_fields.py*
- *script_resolve_old_lts_issues.py*

---

#### PROBABLY OLD AND TO BE REMOVED
2 problems:

#### Error 500 when updating issues

Doesn't work to update issues (like [6760](https://projects.nbis.se/issues/6760)), because the Redmine Surveys 
Notifier plugin crashes when there are `nil` values in the custom fields. No idea why my test issue did not have `nil` values, perhaps since i created it through the web ui and it assigns empty strings instead of `nil`. The other issues seem to be created by the forms or email? (Added by Support Request)

A solution could be to add `.to_s` to the line in the plugin that crashes

```ruby
# in /data/redmine/redmine-3.4/plugins/redmine_surveys_notifier/app/models/surveys_notifier.rb, line 32

::Rails.logger.info("custom field " + field.custom_field.name + " " + field.value.to_s)
```


#### Rejected is counted as closed

The survey notifier plugin regards a status change to `Rejected` as the same as `Closed`, and thus triggers a 
survey email when a issue is rejected. I have not seen any survey email being sent out, so it is a bit unclear 
what happens after the plugin is triggered. The code looks like it should send it if it has triggered, but the mail server shows no email being sent. I can't find where the typeform it links to has been created, so i can't check if anyone has filled it in lately. If there are no responses, is it even being sent out? Hopefully someone should have noticed no responses coming in if that was the case?

Could be solved by adding an exception for thie rejected status. 

```ruby
# in /data/redmine/redmine-3.4/plugins/redmine_surveys_notifier/app/models/surveys_notifier.rb, line 13

if j.prop_key == "status_id" and issue.status.is_closed then

# change to (according to chatgpt)
if j.prop_key == "status_id" and issue.status.is_closed and issue.status.name != "Rejected" then
```
