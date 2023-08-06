
Simple Application
------------------

About this project

This project will help starting an application, which needs to have initialization
step at the beginning (for example: for gathering settings) and use them in many
places/endpoints.
For example, normally you would need to use two separate mechanism for settings
in celery application and web application, because you should not use web
application startup in the celery app. This package provide sollution for this
problem.


