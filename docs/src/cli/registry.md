# Registry

#### Description
`A collection of commands to interact with Image Registry.`

This collection of commands helps in tasks such as pushing and pulling docker images from image registries, including cloud registries like ECR and GCR and Dockerhub.

## Push

```bash
usage: mldock registry push [--dir <path>] [--provider <text>] [--region <text>]
                         [--build] [--tag <text>] [--stage <text>]
```

#### Description
`Push docker container image to Image Registry.`

#### Options

`--dir` path to mldock directory

`--provider` Cloud container provider to push container image to.

`--region` *(Default=None)* Region, specific to provider, where cloud container registry is available.

`--build` (Optional) Flag which tells mldock to build before pushing container image.

`--tag` *(Default=latest)* Selects which container image varient to run container as.

`--stage` *(Optional)* Selects which stage to run docker container in.

## Pull

```bash
usage: mldock registry pull [--dir <path>] [--provider <text>] [--region <text>]
                        [--tag <text>] [--stage <text>]
```

#### Description
`Pull docker container image from Image Registry.`

#### Options

`--dir` path to mldock directory.

`--provider` Cloud container provider to pull container image from.

`--region` *(Default=None)* Region, specific to provider, where cloud container registry is available.

`--tag` *(Default=latest)* Selects which container image varient to run container as.

`--stage` *(Optional)* Selects which stage to run docker container in.
