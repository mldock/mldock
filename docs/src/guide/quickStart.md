# Getting Started Quickly

MLDock is built for getting started quickly. The command line tool comes with helpful boillerplate templates that will get you started developing a production machine learning container image really quickly.

To get started creating your first MLDock ready container image do the following:

## Create your first container image project
1. Install MLDock

The pip install is the only supported package manager at present. It is recommended that you use an environment manager, either virtualenv or conda will work.

```bash
pip install mldock
```

2. Initialize or create your first container

You will see a some of prompts to set up container.

```bash
mldock container init --dir my-first-container
```

::: tip
MLDock's power and versatility lie in using templates to intialize new container image projects quickly. Either use the default container options provided or you can even bring your own. For more information, check out [Initialize a new container from Template](../cli/container.html#initialize).
:::


