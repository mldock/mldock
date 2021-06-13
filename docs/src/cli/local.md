# Local

#### Description
`Tools used for local development including building, training and deploying a dev endpoint.`

## Build

```bash
usage: mldock local build [--dir <path>] [--no-cache] [--tag <text>]
                          [--stage <text>]
```

#### Description
`Build mldock container image locally`

#### Options

`--dir` Path to mldock container project directory.

`--no-cache` (Optional) Flag which forces docker to build container without cache.

`--tag` *(Default=latest)* Selects which container image varient to run container as.

`--stage` *(Optional)* Selects which stage to run docker container in.

## Train

```bash
usage: mldock local train [--dir <path>] [--params --p <param=value>]
                          [--env_vars --e <env_var=value>] [--tag <text>]
                          [--stage <text>]
```

#### Description
`Run training locally on machine`

#### Options

`--dir` Path to mldock container project directory.

`--params -p` *(Optional)* Temporarily set or override a hyperparameter when running container.

`--env_vars -e` *(Optional)* Temporarily set or override a hyperparameter when running container.

`--tag` *(Default=latest)* Selects which container image varient to run container as.

`--stage` *(Optional)* Selects which stage to run docker container in.

## Deploy

```bash
usage: mldock local deploy [--dir <path>] [--port <text>]
                           [--params -p <param=value>]
                           [--env_vars -e <env_var=value>] 
                           [--tag <text>] [--stage <text>]
```

#### Description
`Run deploy locally on machine at localhost`

#### Options

`--dir` Path to mldock container project directory.

`--port` path to payload file

`--params -p` *(Optional)* Temporarily set or override a hyperparameter when running container.

`--env_vars -e` *(Optional)* Temporarily set or override a hyperparameter when running container.

`--tag` *(Default=latest)* Selects which container image varient to run container as.

`--stage` *(Optional)* Selects which stage to run docker container in.

## Predict

```bash
usage: mldock local predict [--payload <path>] [--host <text>]
                            [--content-type <text>]
```

#### Description
`Execute prediction request against ml endpoint`

#### Options

`--host` server url to send request to.

`--payload` path to payload file

`--content-type` *(default=application/json)* how to serialize the payload in the request to the server.
