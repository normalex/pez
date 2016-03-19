### PEZ

Is a REST'ish big numbers dispenser as a service.

All numbers are unique until the underlying sequence generators wrap. This is intentional.

The service exposes the following resources:

**/v1/forward**

Returns a single unsigned integer from an ascending sequence of numbers. Will wrap after reaching *2^63-1*.

**/v1/reverse**

Returns a single unsigned integer from a descending sequence of numbers, aka countdown. Will wrap after reaching 1.

```
curl -s localhost:8000/v1/forward
71

curl -s localhost:8000/v1/reverse
9223372036854775807
```

The v2 API has added an optional parameter **count** by default is limited to 100.

**/v2/forward?count=N**

**/v2/reverse?count=N**

The v2 alwasy returns a list of numbers, even for single numbers.

```
curl -s "localhost:8000/v2/forward?count=5"
[30011, 30012, 30013, 30014, 30015]

curl -s "localhost:8000/v2/forward"
[30016]
```

### Design

* preferably run in the AWS environment

* try to use alternative solution than Mysql REPLACE

* clustered HA transactional storage that won't need actual data to be posted to increment or decrement counters

ElastiCache Memcache won't work as each participating node does not distribute data to others.

ElastiCache Redis wont' work because of poo replication and only 20 backups in 24 hours Amazon limitation.

DynamoDB needs actual data post to increment counter, but does not have anything to support decrement.

Exotic approaches like atomic file Date Time field change and sparse file marker manipulations were dropped as block EBS is per instance only and EFS is still in beta.

## Choosing PostgreSQL on RDS

This DB is a perfect alternative to Mysql as it natively supports SQL SEQUENCE objects.

Each SEQUENCE can be created with a high degree of customization. All operations on sequences are atomic and extremely fast.

There is no need to insert any data into the DB to advance sequence counters.

## Development and deployment

Run **devbootstrap.sh /virtualenv/directory** first to update and install pip and related development requirements.

Coverage is enabled with nosetests and configured in **setup.cfg**

The project is using a slightly modified **vcversioner** module to generate version from git tags and automatically inject

__version__ into the source code.

Included **fabfile.py** has more info on the deployment procedures in its module docstring.

Poor man's profiling can be done the following way:

```
python -m cProfile -o /tmp/sample.profile /virtualenv/directory/bin/gunicorn --reload pez.webapp

and in the second terminal run a **boom** request loader:

boom -c 100 -n 10000 'http://localhost:8000/v2/forward?99'
```

Why not Apache's **ab**?

Well, the standard one from AMI repos does not support dynamic content being returned from PEZ API.

As the primary goal is to host PEZ using OpsWorks, the configuration is controlled through a series of environment variables: PEZ_DB_HOST, PEZ_DB_PORT, PEZ_MAX_COUNT and etc. Consult pez.config module.

## To RPM or Not?

Eventually RPM'ing the project and all it's requirements is quite easy; however to make an elegant CI cycle the custom yum repositories have to be build, deployed and referenced from each new staging environment deployment separately. Having Artifactory with support of inheritance layers would solve much of problems.

## TODO

* atomic staging environment deployment using OpsWorks

* add sphinx doc generator for gh_pages branch

* further explore self documenting resource endpoints, possibly through offline static module injection from sphinx

