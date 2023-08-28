# Installation and setup guide

### Docker engine

For using the application provided by this repository, please make sure to install a **Docker**-engine version > `v20.0.0` .

A detailed installation guide for **Windows**, **Linux** and **macOS** for this software can be found on [the main docker-docs](https://docs.docker.com/engine/install/).

### Docker compose

On top the Docker-engine, a small tool called *docker-compose* is needed in order to orchestrate multiple containers at once. The source-code is written in Python and freely available in the [Official GitHub Group](https://github.com/docker/compose).

> **Note for Windows- and macOS-users**: _If you installed the Docker-engine on macOS or Windows, docker-compose is already included in the distributed version_

> **Note for linux-users**: _You may either install the docker-compose binary from the `apt`-servers via `apt-get install docker-compose` (for Ubuntu 18.04 and later), install it through Python with `pip install docker-compose` if you already have a Python-distribution installed or download the binaries from the [release-page](https://github.com/docker/compose/releases). Detailed instructions can be found on the [Digital Ocean How-to-page](https://www.digitalocean.com/community/tutorial_collections/how-to-install-docker-compose) or the [README from the offical GitHub](https://github.com/docker/compose/tree/v2.15.1#linux).


### Login to Fraunhofer Docker registry

For pulling the Docker-images, you will need to login via commandline on the machine you installed your Docker distribution on. For this procedure you can login either:

* with your general Gitlab-password (_**not** recommended_)
* a generated access-token (_recommended_)

> Note: _If you would like to proceed with an access-token please log into the [Fraunhofer Gitlab](https://gitlab.cc-asp.fraunhofer.de/), navigate to your avatar in the upper right corner and click on `Preferences`. Now, please open the submenu `Access tokens` in the toolbar on the lefthand side. Create a new access token with a new **name** and select the `read_registry`-checkbox. Please store this token in a password-database or elsewhere. You will **not** be able to read it again, when you refresh or close the page. However, you can also add new or delete old access tokens. For this application, you will only need it once for downloading the images. You might need to refresh or add a new token, when you want to update your docker images after the token as expired._
![token](_static/img/tokens.jpg)

Type in:

```docker login registry.gitlab.cc-asp.fraunhofer.de/reaxpro```

Use your username, *as it is displayed _after_ the @ under your Gitlab avatar in right left corner* and your password or access-token.

If successfull, you should see the following traceback:

`Login Succeeded`

> Note: The message:
 `WARNING! Your password will be stored unencrypted in /home/<user>/.docker/config.json` is normal when you do not use a credential helper. This is also why an access-token is recommended for logging into the registry, since it can be easiliy removed and expires automatically after a given amount of time.

### Setup the files

Make a new file called `.env` and add it to a directory of your choice. This is going to be your **runtime**-directory.

> Note: _If you cloned the source code of this repository, you may simply copy the `.env.template` into a new file called `.env`._

If you did not clone the repository from source and wrote a new empty file as written above, make sure that your `.env`-file has the following content:

```
PORT=8080
DOCKER_REAXPRO_VERSION=v1.0.0
BASE_IMAGE_TAG=v1.0.0
DOCKER_BUILD_TARGET=production
DOCKER_REAXPRO_IMAGE=registry.gitlab.cc-asp.fraunhofer.de/reaxpro/fastapi-celery
BASE_IMAGE=registry.gitlab.cc-asp.fraunhofer.de/simphony/wrappers/reaxpro-wrappers
CELERY_SCHEMAS="osp.models.co_catalyticfoam:COCatalyticFOAMModel | osp.models.energy_landscape:EnergyLandscape"
CELERY_WORKER_MAPPING="ContinuumCalculation:simphony-catalyticfoam|LandscapeRefinement:simphony-ams"
AMSHOME=/data/volume_1/Software/ams2022
ADFHOME=/data/volume_1/Software/ams2022
ADFBIN=/data/volume_1/Software/ams2022/bin
AMSBIN=/data/volume_1/Software/ams2022/bin
AMSRESOURCES=/data/volume_1/Software/ams2022/atomicdata
ADFRESOURCES=/data/volume_1/Software/ams2022/atomicdata
SCMLICENSE=/data/volume_1/Software/ams2022/license.txt

```

> Note: _The `BASE_IMAGE_TAG` may be bumped to another version from time to time. If a new version shall be used, please update the version number and re-run the following steps of this guide in order to bring up the newest containers._

Now, we check the content of our docker-compose-file. If you did not clone from source, make a new file called `docker-compose.yml` and make sure that it has the following content:

```
version: "3"

services:
  fastapi:
    image: "${DOCKER_REAXPRO_IMAGE:-fastapi-celery}:${DOCKER_REAXPRO_VERSION:-latest}"
    ports:
      - "${PORT:-8080}:8080"
    environment:
      CELERY_REDIS_TYPE: redis
      CELERY_REDIS_HOST: redis
      CELERY_REDIS_PORT: 6379
      CELERY_REDIS_DB: 2
      CELERY_AUTHENTICATION_DEPENDENCIES: ${AUTHENTICATION_DEPENDENCIES}
      CELERY_SCHEMAS: ${CELERY_SCHEMAS}
      CELERY_WORKER_NAME: simphony-workflows
      APP_MODE: server
    volumes:
      - diskcache:/tmp:rw
    depends_on:
      - redis
    networks:
      - reaxpro

  headworker:
    image: "${DOCKER_REAXPRO_IMAGE:-fastapi-celery}:${DOCKER_REAXPRO_VERSION:-latest}"
    environment:
      CELERY_REDIS_TYPE: redis
      CELERY_REDIS_HOST: redis
      CELERY_REDIS_PORT: 6379
      CELERY_REDIS_DB: 2
      CELERY_WORKER_MAPPING: ${CELERY_WORKER_MAPPING}
      CELERY_WORKER_NAME: simphony-workflows
      APP_MODE: worker
    volumes_from:
      - fastapi:rw
    depends_on:
      - redis
    networks:
      - reaxpro

  catalyticfoam:
    image: "${BASE_IMAGE:-simphony-reaxpro}:${BASE_IMAGE_TAG:-latest}"
    environment:
      REAXPRO_CELERY_WORKER_NAME: simphony-catalyticfoam
      REAXPRO_CELERY_WRAPPER_NAME: osp.wrappers.simcatalyticfoam:SimCatalyticFoamSession
      REAXPRO_REDIS_TYPE: redis
      REAXPRO_REDIS_HOST: redis
      REAXPRO_REDIS_PORT: 6379
      REAXPRO_REDIS_DB: 2
    volumes_from:
      - fastapi:rw
    depends_on:
      - redis
    networks:
      - reaxpro

  ams:
    image: "${BASE_IMAGE:-simphony-reaxpro}:${BASE_IMAGE_TAG:-latest}"
    environment:
      REAXPRO_CELERY_WORKER_NAME: simphony-ams
      REAXPRO_CELERY_WRAPPER_NAME: osp.wrappers.simams.simams_session:SimamsSession
      REAXPRO_REDIS_TYPE: redis
      REAXPRO_REDIS_HOST: redis
      REAXPRO_REDIS_PORT: 6379
      REAXPRO_REDIS_DB: 2
      AMSHOME: ${AMSHOME}
      ADFHOME: ${ADFHOME}
      ADFBIN: ${ADFBIN}
      AMSBIN: ${AMSBIN}
      AMSRESOURCES: ${AMSRESOURCES}
      ADFRESOURCES: ${ADFRESOURCES}
      SCMLICENSE: ${SCMLICENSE}
    volumes_from:
      - fastapi:rw
    volumes:
      - ${AMSHOME}:${AMSHOME}:rw
      - ${AMSRESOURCES}:${AMSRESOURCES}:rw
      - ${SCMLICENSE}:${SCMLICENSE}:rw
    depends_on:
      - redis
    networks:
      - reaxpro

  redis:
    image: redis:latest
    volumes:
      - redis-data:/data
    networks:
      - reaxpro

volumes:
  redis-data:
  diskcache:

networks:
  reaxpro:

```

### Pull the latest images

In order to download the latest images, navigate with your commandline into the **runtime**-directory with your `.env` and `docker-compose.yml`.

Simply type:

`docker-compose pull`

Expected output:

```
WARNING: The AUTHENTICATION_DEPENDENCIES variable is not set. Defaulting to a blank string.
Pulling redis         ... done
Pulling fastapi       ... done
Pulling ams           ... done
Pulling catalyticfoam ... done
Pulling headworker    ... done
```

> **Troubleshooting**:
>
> `Can't find a suitable configuration file in this directory or any parent. Are you in the right directory?`
>
> You are not in the **runtime**-directory with the `.env`- or `docker-compose.yml`-file
>
> ---
>
> `ERROR: for simphony  pull access denied for simphony-reaxpro, repository does not exist or may require 'docker login': denied: requested access to the resource is denied`
>  
> You did not place the `.env`-file in the same directory as your `docker-compose.yml` or docker could not source the `.env`-file (due to a potential syntax-error).
>

### Bring up the containers

Simply type:

`docker-compose up -d`

Expected output:

```
WARNING: The AUTHENTICATION_DEPENDENCIES variable is not set. Defaulting to a blank string.
Creating network "fastapi-celery_reaxpro" with the default driver
Creating volume "fastapi-celery_redis-data" with default driver
Creating volume "fastapi-celery_diskcache" with default driver
Creating fastapi-celery_redis_1 ... done
Creating fastapi-celery_fastapi_1 ... done
Creating fastapi-celery_catalyticfoam_1 ... done
Creating fastapi-celery_headworker_1    ... done
Creating fastapi-celery_ams_1           ... done
```

Check if the containers are running by displaying their process status through typing:

```
docker-compose ps
```

> **Note**: _Make sure you type this command in your **runtime**-directory!_

Expected output:
```
             Name                           Command               State                    Ports  
------------------------------------------------------------------------------------------------------------------
fastapi-celery_ams_1             /bin/bash -c -l celery -A  ...   Up  
fastapi-celery_catalyticfoam_1   /bin/bash -c -l celery -A  ...   Up  
fastapi-celery_fastapi_1         ./docker_entrypoint.sh           Up      0.0.0.0:8080->8080/tcp,:::8080->8080/tcp
fastapi-celery_headworker_1      ./docker_entrypoint.sh           Up      8080/tcp  
fastapi-celery_redis_1           docker-entrypoint.sh redis ...   Up      6379/tcp  
```

You may now launch `localhost:8080/docs` in your browser:

![swagger](_static/img/swagger-ui.JPG)

### Stop the containers

Simply type:

`docker-compose stop`

### Remove the containers

Simply type:

`docker-compose down`

### Run with singularity

Instead of using `Docker`, you may also use [`Singularity`](https://docs.sylabs.io/guides/latest/user-guide/)

There are also tools like `singularity-compose`, which can help you composing the containers built by `Docker` through `Singularity`.
For this purpose, please read the [offical documentation](https://singularityhub.github.io/singularity-compose/#/).

**Without** `singularity-compose`, you can also run the containers in a plain bash-script like:

```
#!/bin/bash

# source env-file
source .env

# Define environment variables
DOCKER_REAXPRO_IMAGE="${DOCKER_REAXPRO_IMAGE:-fastapi-celery}"
DOCKER_REAXPRO_VERSION="${DOCKER_REAXPRO_VERSION:-latest}"
PORT="${PORT:-8080}"
AUTHENTICATION_DEPENDENCIES="${AUTHENTICATION_DEPENDENCIES}"
CELERY_SCHEMAS="${CELERY_SCHEMAS}"
CELERY_WORKER_MAPPING="${CELERY_WORKER_MAPPING}"
BASE_IMAGE="${BASE_IMAGE:-simphony-reaxpro}"
BASE_IMAGE_TAG="${BASE_IMAGE_TAG:-latest}"
AMSHOME="${AMSHOME}"
ADFHOME="${ADFHOME}"
ADFBIN="${ADFBIN}"
AMSBIN="${AMSBIN}"
AMSRESOURCES="${AMSRESOURCES}"
ADFRESOURCES="${ADFRESOURCES}"
SCMLICENSE="${SCMLICENSE}"

# Create Singularity containers
singularity exec docker://redis:latest redis-server --daemonize yes

singularity run docker://"$DOCKER_REAXPRO_IMAGE":"$DOCKER_REAXPRO_VERSION" \
  -e CELERY_REDIS_TYPE=redis \
  -e CELERY_REDIS_HOST=redis \
  -e CELERY_REDIS_PORT=6379 \
  -e CELERY_REDIS_DB=2 \
  -e CELERY_AUTHENTICATION_DEPENDENCIES="$AUTHENTICATION_DEPENDENCIES" \
  -e CELERY_SCHEMAS="$CELERY_SCHEMAS" \
  -e CELERY_WORKER_NAME=simphony-workflows \
  -e APP_MODE=server \
  -v diskcache:/tmp \
  -p "$PORT":8080 \
  --network reaxpro &

singularity run docker://"$DOCKER_REAXPRO_IMAGE":"$DOCKER_REAXPRO_VERSION" \
  -e CELERY_REDIS_TYPE=redis \
  -e CELERY_REDIS_HOST=redis \
  -e CELERY_REDIS_PORT=6379 \
  -e CELERY_REDIS_DB=2 \
  -e CELERY_WORKER_MAPPING="$CELERY_WORKER_MAPPING" \
  -e CELERY_WORKER_NAME=simphony-workflows \
  -e APP_MODE=worker \
  --volumes-from fastapi:rw \
  --network reaxpro &

singularity run docker://"$BASE_IMAGE":"$BASE_IMAGE_TAG" \
  -e REAXPRO_CELERY_WORKER_NAME=simphony-catalyticfoam \
  -e REAXPRO_CELERY_WRAPPER_NAME=osp.wrappers.simcatalyticfoam:SimCatalyticFoamSession \
  -e REAXPRO_REDIS_TYPE=redis \
  -e REAXPRO_REDIS_HOST=redis \
  -e REAXPRO_REDIS_PORT=6379 \
  -e REAXPRO_REDIS_DB=2 \
  --volumes-from fastapi:rw \
  --network reaxpro &

singularity run docker://"$BASE_IMAGE":"$BASE_IMAGE_TAG" \
  -e REAXPRO_CELERY_WORKER_NAME=simphony-ams \
  -e REAXPRO_CELERY_WRAPPER_NAME=osp.wrappers.simams.simams_session:SimamsSession \
  -e REAXPRO_REDIS_TYPE=redis \
  -e REAXPRO_REDIS_HOST=redis \
  -e REAXPRO_REDIS_PORT=6379 \
  -e REAXPRO_REDIS_DB=2 \
  -e AMSHOME="$AMSHOME" \
  -e ADFHOME="$ADFHOME" \
  -e ADFBIN="$ADFBIN" \
  -e AMSBIN="$AMSBIN" \
  -e AMSRESOURCES="$AMSRESOURCES" \
  -e ADFRESOURCES="$ADFRESOURCES" \
  -e SCMLICENSE="$SCMLICENSE" \
  --volumes-from fastapi:rw \
  -v "$AMSHOME":"$AMSHOME":rw \
  -v "$AMSRESOURCES":"$AMSRESOURCES":rw \
  -v "$SCMLICENSE":"$SCMLICENSE":rw \
  --network reaxpro

```
