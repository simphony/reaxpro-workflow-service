# ReaxPro Workflow Service

A simple [FastAPI-framework](https://fastapi.tiangolo.com/) for running asynchronous tasks through [python-celery](https://pypi.org/project/celery/). This app is targeted to be a high-level API for the workflow-orchestration of the [ReaxPro-platform](https://www.reaxpro.eu/).

## Authors

[Matthias Büschelberger](mailto:matthias.bueschelberger@iwm.fraunhofer.de) (Fraunhofer Institute for Mechanics of Materials IWM)
[Kiran Kumaraswamy](mailto:kiran.kumaraswamy@iwm.fraunhofer.de) (Fraunhofer Institute for Mechanics of Materials IWM)

## Documentation

Please refer to the [ReadTheDocs-pages](https://reaxpro.pages.fraunhofer.de/docs/) for the overall installation procedure, tutorials and use case documentation.

## Python dependencies

First of all, you will need to install OSP-core

```shell
(env) user@computer:~$ pip install osp-core
```

Then, install the wrapper. Simply type:

```shell
(env) user@computer:~$ pip install reaxpro-workflow-service
```

... or if you are installing from source (cloning of the repository needed before):


```shell
(env) user@computer:~/reaxpro-workflow-service$ pip install .
```

## License

This project is licensed under the BSD 3-Clause. See the LICENSE file for more information.

## Disclaimer

Copyright (c) 2014-2023, Fraunhofer-Gesellschaft zur Förderung der angewandten Forschung e.V. acting on behalf of its Fraunhofer IWM.

Contact: [SimPhoNy](mailto:simphony@iwm.fraunhofer.de)
