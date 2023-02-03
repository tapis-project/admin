from jinja2 import Environment, PackageLoader, select_autoescape
import yaml

# By default, we include all services except Authenticator which requires a username/password
# for the token check.
DEFAULT_SERVICES = ['actors', 'apps', 'files', 'globus_proxy', 'jobs', 'meta', 
'notifications', 'pods', 'sk', 'streams', 'systems', 'tenants', 'tokens', 'workflows']

DEFAULT_HEALTHCHECK_INTERVAL = "15s"

DEFAULT_SERVICECHECK_INTERVAL = "1m"

env = Environment(
    loader=PackageLoader("compile"),
    autoescape=select_autoescape()
)

template = env.get_template("config.yaml.j2")
with open("/endpoints.yaml", 'r') as f:
    endpoints = yaml.safe_load(f)

for tenant in endpoints['tenants']:
    if 'services' not in tenant.keys():
        tenant['services'] = DEFAULT_SERVICES
    if not 'healthcheck_interval' in tenant.keys():
        tenant['healthcheck_interval'] = DEFAULT_HEALTHCHECK_INTERVAL
    if not 'servicecheck_interval' in tenant.keys():
        tenant['servicecheck_interval'] = DEFAULT_SERVICECHECK_INTERVAL


s = template.render(**endpoints)

if __name__ == "__main__":
    print(s)
