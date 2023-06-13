# Tapis admin #

This repository contains helpful scripts, utlities and applications for administering Tapis 
installations. The following directories are included:

1. ``notebooks`` -- This folder contains Python notebooks that document common administrative tasks such as as creating new tenants or configuring authentication in the Tapis Authenticator. In general, these notebooks make use of the Tapis Python SDK (tapipy) and require privileged access to the Tapis installation. 

2. ``status`` -- This folder contains the Tapis Status application, a simple web application that runs HTTP requests on a configurable time interval and checks the basic health of each service. The dashboard provides an overview page with green/red statuses allowing an administrator to get a quick look at the health of all services. The application is configurable, allowing administrators to specify which endpoints and tenants should be monitored.

3. ``util`` -- This folder contains Python programs and utilities helpful for administrative tasks, such as checking which Tapis images/versions are running in your Tapis installation. Typically, the utils contains programs that need to run "headless" and thus could be difficult to run as Python notebooks.

