# redmine_utils

2 problems:

#### Error 500 when updating issues

Doesn't work to update issues (like [6760](https://projects.nbis.se/issues/6760)), because the Redmine Surveys Notifier plugin crashes when there are `nil` values in the custom fields. No idea why my test issue did not have `nil` values, perhaps since i created it through the web ui and it assigns empty strings instead of `nil`. The other issues seem to be created by the forms or email? (Added by Support Request)

A solution could be to add `.to_s` to the line in the plugin that crashes

```ruby
# in /data/redmine/redmine-3.4/plugins/redmine_surveys_notifier/app/models/surveys_notifier.rb, line 32

::Rails.logger.info("custom field " + field.custom_field.name + " " + field.value.to_s)
```


#### Rejected is counted as closed

The survey notifier plugin regards a status change to `Rejected` as the same as `Closed`, and thus triggers a survey email when a issue is rejected. I have not seen any survey email being sent out, so it is a bit unclear what happens after the plugin is triggered. The code looks like it should send it if it has triggered, but the mail server shows no email being sent. I can't find where the typeform it links to has been created, so i can't check if anyone has filled it in lately. If there are no responses, is it even being sent out? Hopefully someone should have noticed no responses coming in if that was the case?

Could be solved by adding an exception for thie rejected status. 

```ruby
# in /data/redmine/redmine-3.4/plugins/redmine_surveys_notifier/app/models/surveys_notifier.rb, line 13

if j.prop_key == "status_id" and issue.status.is_closed then

# change to (according to chatgpt)
if j.prop_key == "status_id" and issue.status.is_closed and issue.status.name != "Rejected" then
```
