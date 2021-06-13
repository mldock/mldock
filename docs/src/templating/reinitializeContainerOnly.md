# Re-Initialize container only

Any provider of software services knows that you want to build something new, you should also maintain it. A big part of a challenge comes when migrating our code or platforms or updating dependencies. As the number of container you support increases, so does the tedium and difficulty of the task increase.

MLDock to the rescue. :ambulance:. MLDock command line provides a `--container-only` flag that can be used with the [Initialize](../cli/container.html#initialize) command to restrict the intialization to only scripts contained in `/container` directory and protecting the user defined scripts at the `/src` level in the container project.

Below we cover a few use-cases for this feature

## Updating to and Running a custom server

Often teams would like to support a standard server implementation across all projects. For example, tensorflow server or pytorch or kubeflow server. If you had to update all your ml container projects this might be painful. Instead, building a single template which implements the new server and then just `re-initializing` the container project with `--container-only` raised could greatly streamline this task.

This can be achieved with following workflow:

1. Create a new project as a basis for your new container implementation.

``` bash
mldock container init --dir <new-project-name>
```

2. Update the code in `new-project-name/src/container/prediction/` to implement your new server

3. Create a template from your new project containing the new server

``` bash
mldock container create-template --dir <new/project/name> --name <new-server-template-name> --out <destination/path/to/template>
```

4. Finally, update your old project

``` bash
mldock container init --dir <new/project/name> --container-only --no-prompt --template <destination/path/to/template/template-name>
```





## Migrating containers to new platforms <Badge text="beta" type="warning"/>

Fundamtentally, the `/container` scripts incorporate platform specific installs and configuration to help them run. An MLDock container project can easily be updated to be deployed on any of the supported platforms.

For example, imagine your team has been tasked with "Migrating all your containers to run on Kubernetes, where they currently run on Amazon Sagemaker". Thankfully, with MLDock this can be achieved by running the following command:

``` bash
mldock container init --dir <path/to/mldock/project> --container-only
```

And follow the prompts to update the `{platform: Sagemaker}` -> `{platform: kubernetes}`

