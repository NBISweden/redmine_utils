# Dedicated task scripts. Typically run by Martin D:

## *script_send_out_user_survey_to_closed_projects.py* 
Will send an email to the `pi_email` of all projects that 
have been either closed or resolved in the specifed date range. Will only send to projects that have the 
checkbox `send_user_survey` checked. After the email is sent, the checkbox will be unchecked to avoid sending 
multiple emails, as well as updating the project description to indicate that the survey has been sent.
```bash
python3 script_send_out_user_survey_to_closed_projects.py -c config.yaml -s 2025-03-04 -e 2025-10-12
```

### Last run

To keep track of start and end points.
```bash
# for biif
python3 scripts/script_send_out_user_survey_to_closed_projects.py -d -v -c config.yaml -n "BioImage Informatics" -i 8034,8000,7871,8076,7632,7837,6797,6763,7402,7649,8027,7629,7185

# for nat.bioinfo.supp and long-term
python3 scripts/send_out_user_survey_to_closed_projects.py -c config.yaml -s 2025-10-12 -e 2026-03-18
```

### TODO

* For next time (spring 2026), only look for resolved issues.
  * Or maybe we should include closed then as well? The `send_survey_when_closed` checkbox will be unticked for the ones we sent to now, and people might make mistakes and close an issue directly without passing through resolved first.
* Refactor the script to be stuctured more in functions to keep `main` lean.
* Use a fuction user with the proper permissions to interact with redmine.

## Other scripts
- *script_bengt_vr_lifespan_stats.py* 
- *script_copy_values_between_fields.py*
- *script_resolve_old_lts_issues.py*

