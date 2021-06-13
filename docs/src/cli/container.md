# Container

#### Description
`Container project tools for creating new templates, updating and initializing new containers.`

## Initialize

```bash
usage: mldock container init [--dir <path>] [--no-prompt] 
                         [--template <path>] [--container-only]
                         [--testing-framework] [--service]
```

#### Description
`Tnitialize mldock enabled container`

#### Options

`--dir` Path to mldock container project directory.

`--template` Path to mldock supported container template.

`--no-prompt` *(Optional)* Flag which tells mldock to run init process non-interactively.

`--container-only` *(Optional)* Flag which tells mldock to only initialize or update the container code scripts.

`--testing-framework` *(Optional)* Selects which container image varient to run container as.

`--service` *(Optional)* Selects which stage to run docker container in.

::: tip
Mldock is streamlined for building new projects from standard templates. Think about Starting new projects based
on standard templates which could include using your preferred server, or special platform requirements like boto3 or gcloud and so on.
:::

::: details
Expects an mldock supported container template. See [Create Template](./container.html#create-template)

Using an available mldock template such as:

```./my_templates/awesome-template```

and running:

```mldock container init --dir=awesome-project --template=./my_templates/awesome-template```

Will create your new project based on an previous template or project

:::


## Create Template

```bash
usage: mldock container create_template [--dir <path>] [--name <text>]
                                    [--out <path>]
```

#### Description
`Create a mldock enabled container template.`

`Tnitialize mldock enabled container`

#### Options

`--dir` Path to mldock container project directory.

`--name` Name of new template to create.

`--out` Path to save mldock container template to.

::: details
Given 

```mldock --dir=my-container-project --name=awesome-template --out=./my_templates```

Would yield a mldock template 

```./my_templates/awesome-template```

To create a new project from your template see [Initialize Project](./container.html#initialize).
:::

## Update

```bash
usage: mldock container update [--dir <path>]
```

#### Description
`Update mldock container configuration.`

`--dir` Path to mldock container project directory.


## Summary

```bash
usage: mldock container summary [--dir <path>]
```

#### Description
`Show summary for mldock container.`

`--dir` Path to mldock container project directory.
