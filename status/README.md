# Tapis Monitoring Application and Status Dashboard 

A configurable monitoring application and status page for Tapis v3 based on the Gatus project (https://gatus.io).

## How to Use
There are three steps to using this repository. 

1) First, create an endpoints.yaml file with the configuration you want. The yaml file should 
include a single `tenants` stanza which is a list of tenants to configure checks for. Each
tenant in the list can include the following attributes:
  - `base_url`: used to make the request
  - `display`: added to the name of each endpoint on the status page.
  - `jwt`: A valid JWT for the tenant; used for endpoint checks that required auth.
  - `services`: A list of Tapis v3 services to monitor. If not provided, a default set is included.
  - `healthcheck_interval`: How often to check healthcheck endpoints; default is 15s.
  - `servicecheck_interval`: How often to check service endpoints; default is 1m.
  - `authn_username`: A valid username for the tenant; used for the Authenticator token generation check.
  - `authn_password`: Corrsponding password for `authn_username`; used for the Authenticator token generation check.

See the `endpoints-minimal-ex.yaml` and the `endpoints-complex-ex.yaml` for some examples. (NOTE:
the examples are missing the JWTs and passwords...)

2) Use the image `tapis/status-config-builder` to build a Gatus config from the `endpoints.yaml` 
as follows:

```
docker run --rm -it -v $(pwd)/endpoints.yaml:/endpoints.yaml tapis/status-config-builder 
```
The status page config file will be printed to the screen and you can redirect stdout to a file, e.g.:

```
docker run --rm -it -v $(pwd)/endpoints.yaml:/endpoints.yaml tapis/status-config-builder > config.yaml
```

Or, run a shell in the container if you need to debug:
```
docker run --rm -it -v $(pwd)/endpoints.yaml:/endpoints.yaml tapis/status-config-builder bash
```
and execute the python program directly:
```
python compile.py
```

3) Finally, with your `config.yaml` file generated, use the docker-compose file to start up the 
status app:

```
docker-compose up
```


## Developing the Project

To develop this project, make code changes and then create a new container image with:
```
docker build -t tapis/status-config-builder .
```

All of the actual checks/tests are in the `config.yaml.j2` file. Simply add new tests by 
writing some Jinja2 template code there and then recompile the image using the Docker build
command above. 