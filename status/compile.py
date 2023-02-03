from jinja2 import Environment, PackageLoader, select_autoescape
import yaml

DEFAULT_SERVICES = ['apps', 'jobs', 'systems', ]

env = Environment(
    loader=PackageLoader("compile"),
    autoescape=select_autoescape()
)

template = env.get_template("config.yaml.j2")
with open("/endpoints.yaml", 'r') as f:
    endpoints = yaml.safe_load(f)

for tenant in endpoints['tenants']:
    if 'services' not in tenant.keys():
        tenant.services = DEFAULT_SERVICES

s = template.render(**endpoints)

if __name__ == "__main__":
    print(s)
