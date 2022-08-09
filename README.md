# A Class' SSH Server in Kubernetes 

Since the dawn of the modern operating system, computer classes have used a shared login server to create a work environment for students. In the cloud era we've used virtual machines in place of physical servers (IaaS) to make our workloads more convenient to manage. But, our severs are still *pets*, they are precious to us, because they are stateful appliances running bespoke applications with some real problems: 

1. They are a single point of failure that impacts our ability to teach. 
1. Students are a security risk. I once caught a student who was able to maintain access after the end of a term. 
1. Management tools like VMware are clunky compared to cloud vendors. 
1. Cloud vendors are expensive for this kind of workload. 

This project is a way to deploy a traditional login server into a Kubernetes cluster. I started working on it as a way to get a deeper understanding of cloud-native computing.
 
## Quickstart 

You should have a Kubernetes cluster already built and `kubectl` and `helm` installed and configured. 

1. Add this Helm repo: 

    ```console
    $ helm repo add cloud-native-server https://mike-matera.github.io/cloud-native-server/
    $ helm repo update
    ```

1. Generate an SSH CA key: 

    ```console
    $ ssh-keygen -t rsa -f ca_key -N ''
    ```

1. Sign your SSH public key using the CA key. This creates a certificate you can use to login to your server. 

    ```console
    cp ~/.ssh/id_rsa.pub . 
    ssh-keygen -s ./ca_key -I admin-key -n $USER ./id_rsa.pub
    ```
  
1. Use `helm` to deploy your server: 

    ```console 
    $ helm install myserver cloud-native-server/cloud-server \
      --set user=$USER \
      --set hostName=myhost \
      --set-file ssh.ca_key=./ca_key,ssh.ca_key_pub=./ca_key.pub
    ```

1. Wait for the application to deploy and check the service IP:

    ```console
    $ kubectl get service
    NAME                    TYPE           CLUSTER-IP       EXTERNAL-IP    PORT(S)        AGE
    test-ssh-cloud-server   LoadBalancer   10.152.183.173   172.20.2.100   22:31456/TCP   5s
    ```

    Login using the IP address:

    ```console
    $ ssh -o CertificateFile=./id_rsa-cert.pub $USER@172.20.2.100  
    ```

1. Cleanup is a two step process because home directories are preserved between application installs and uninstalls to protect user's precious data. 

    1. Uninstall the Helm chart:

        ```console 
        $ helm uninstall myserver 
        ``` 

    1. Delete home directories: 

        ```console 
        $ kubectl delete pvc home-myserver-cloud-server-0
        ```

## Chart Parameters 

The following table shows the configuration options available in `cloud-server/values.yaml`. Most configuration tasks can be accomplished using these values: 

### Global Parameters 

| Name | Description | Value | 
| --- | --- | --- | 
| `homeSize` | Size of the `/home` mount | `2Gi` | 
| `homeStorageClassName` | Storage class for the home mount | `""` | 
| `user` | The username of the default user | `"human"` |  
| `userID` | The UID of the default user | `10000` |
| `hostName` | The hostname | `"myserver"` |
| `userSSHKey` | An SSH public key that will be added to authorized_keys of the default user. | `""` |
| `userSSHImport` | Import default user keys with `ssh-import-id` | `""` | 
| `customizeRepo` | A repository that will be checked out on boot. | `""` | 
| `customizeRepoCommand` | A command to run in the repository named in `customizeRepoCommand`. | `""` | 
| `customizeCommand` | Run this command in the default user's home directory if it exists. | `""` | 
| `privileged` | Create a privileged container. **See the "Security" section for details** | `true` |  

### SSH Parameters 

| Name | Description | Value | 
| --- | --- | --- | 
| `ssh.ca_key` | An SSH private key for signing SSH certificates | None/Required | 
| `ssh.ca_key_pub` | The corresponding public key for `ssh.ca_key` | None/Required | 
| `ssh.existingSecret` | An existing secret with keys `ca_key` and `ca_key_pub`. The other settings are ignored if this one exists. | None/Required | 

### Image Options 

| Name | Description | Value | 
| --- | --- | --- | 
| `image.repository` | The image repository for the container. |	`ghcr.io/mike-matera/cloud-native-server` | 
| `image.tag` | Container image tag. Change this for different distros. | `jammy-2022070801` | 
| `image.pullPolicy` | 	Image pull policy	| `IfNotPresent` | 
| `image.pullSecrets` | Specify docker-registry secret names as an array | `[]` | 

### Customizing Mounts 

You can add mounted volumes to your container. This is useful when you want to keep some persistent data separate from other persistent data. For example you might have a home directory structure that separates students depending on what class they're enrolled in.

```yaml
extraMounts:
  - name: cis90
    path: /home/cis90
    size: 1Gi 
    className: hdd
  - name: cis91
    path: /home/cis91
    size: 1Gi 
    className: hdd
```

The `extraMounts` array will create a `PersistentVolumeClaim` for each entry. All of the fields are required (including the one for the storageClass name).

### Customizing Ports 

If you want your sever to be able to handle incoming connections on more than just port 22 for SSH you can specify them using the `extraPorts` key in your `custom.yaml` file. For example if you want to run a web server you could add:

```yaml
extraPorts:
  - port: 80
    proto: TCP
    name: http
  - port: 443
    proto: TCP
    name: https  
```

All of the fields are required (including `proto` and `name` which is an arbitrary identifier)

## System Configuration 

There are three stages where configuration can be inserted:

1. Executing an arbitrary command in the default user's home directory. This is the most flexible stage. 
1. The execution of `/etc/rc.local` on boot. This stage customizes the image with SSH keys and creates the admin user. 
1. The `Dockerfile` build. The purpose of this stage is have a functional base container with most of good stuff installed. This is the least flexible stage. 

The next sections describe how to customize each stage. 

### User Customization 

The default `/etc/rc.local` script uses variables that placed in the `/etc/rc.env` file. The following customization variables become environment variables at startup: 

  | Chart Variable | Environment Variable | Default | 
  | --- | --- | --- |
  | `user` | `DEFAULT_USER` | `human` |
  | `userSSHKey` | `DEFAULT_KEY` | | 
  | `userSSHImport` | `DEFAULT_KEY_IMPORT` | |  
  | `hostName` | `SET_HOSTNAME` | `myserver` | 
  | `customizeRepo` | `CUSTOMIZE_REPO` | | 
  | `customizeRepoCommand` | `CUSTOMIZE_REPO_COMMAND` | | 
  | `customizeCommand` | `CUSTOMIZE_COMMAND` | | 
  
Content added to the `rcEnv` key in your `custom.yaml` file will be appended to `/etc/rc.env`. The environment variables in `/etc/rc.env` are defined during system start and during user customization. This is a good place to put API keys and other secrets that might be useful during customization. 

The `/etc/rc.local` script does the following:

1. Sets the hostname if possible. 
1. Creates the default user. 
1. Executes the `/etc/rc.user` script as the default user. 

The `/etc/rc.user` script does the following: 

1. Installs SSH keys into the user's account (see `userSSHKey` and `userSSHImport`)
1. Checks out `customizeRepo` into a temporary directory and runs `customizeRepoCommand` 
1. Runs `customizeCommand` 

Errors in `/etc/rc.user` are ignored. If they occur the container may not work but will become ready. 

#### Why do user customization? 

1. This is the easiest way to customize your server. Try this first. 

### Customizing Boot 

The images use `systemd` to run the classic `rc.local` script. This works well because there's existing infrastructure so not much image customization has to be done. The `sshd` service has been updated to wait for the `rc-local` service to finish, because SSH keys are generated by `/etc/rc.local`. The contents of `/etc/rc.local` and `/etc/rc.user` are in the Helm chart. You can update the script by adding the following key to `custom.yaml`:

```yaml
rcLocal: |
  #! /usr/bin/bash
  set -e 

  . /etc/rc.env 
  
  [...your code here...]
```

You should look at the existing code in `cloud-server/values.yaml`. There are a few important things that the `rc.local` script must do: 

1. Set the hostname 
1. Create SSH host keys and sign them with the SSH CA key 
1. Create the admin user, make sure they have `sudo` access and install their SSH public keys 
1. Any personal customization 
1. Touch the `/ready` file to tell kubernetes that the container is ready. 

#### Why customize boot? 

1. If you have a non-Ansible way to deliver customization, i.e. Puppet or Chef networks.

### Custom Docker Images 

You can find the `Dockerfile` for the supported distros in the `containers` directory. If you clone this repository on GitHub you can reuse the `.github/workflows/*` files to build your own packages. Container builds are triggered by certain tags. For example, the Ubuntu container is build on a `jammy-*` tag. 

If you use a custom image, create a values file called `custom.yaml` and add the following lines to it:

```yaml
image:
  repository: ghcr.io/your-github-name-here/cloud-native-server
  tag: "your-tag-here"
```

Helm will then deploy your custom image. 

#### Why customize the image? 

1. If you want **a lot** of new or different packages installed. You can install packages during the user customization stage. 
1. If you want to use Puppet or Chef instead of Ansible.
1. If you want to use a non-supplied distro. 
 
## Security 

This project was inspired by running [LXD](https://linuxcontainers.org/lxd/introduction/) containers for the last few years. They took the place of VMware VMs and I was really happy with how much easier they are to build and manage. I started to wonder, *would it be possible to run `systemd` in an unprivileged container in Kubernetes?* It turns out the answer is no (I will explain this in detail at some point). This project runs `systemd` in a privileged container, but also supports unprivileged containers by launching `sshd` directly without `systemd`. 

Containerization is not a security technology. Running untrusted workloads --like a student shell-- carries a greater risk than running the same workload in a VM. But containers are lighter, more flexible and convenient, more robust and resilient than VMs. Until Kubernetes supports [user namespaces](https://kinvolk.io/blog/2020/12/improving-kubernetes-and-container-security-with-user-namespaces/) a container escape from a privileged container means the attacker has full control of the node. 

There is one essential question to consider when you deploy this project: 

> Will you give *untrusted* users `sudo` access? 

The next sections will show you how to configure the application based on the answer to the question above. 

### I Only Have Trusted `root` Users 

**Run the privileged version.** This the default. You can set the privileged setting in your `custom.yaml` file: 

```console
$ helm install .... --set privileged=true 
```

This results in a very VM-like system. Users login and get a personal `cgroup` and can see each other with the `who` and `w` commands. The system runs normally with periodic security updates, `cron` and all of the things you'd expect. But, the container runs as root on the node so a container escape is serious. Container escapes are harder --maybe impossible-- as a non privileged user on your system. 

### I'm Giving Students `sudo` Access 

**Run the unprivileged version.**

```console
$ helm install .... --set privileged=false
```

This results in a system that's only running `sshd`. The Kubernetes deployment overrides the container's entrypoint do to this. Many things will still work and the user has `sudo` access. The container itself is running as an unprivileged user so a container escape is far less damaging. 

### The Hostname and `CAP_SYS_ADMIN` 

Annoyingly, in order to set the hostname *inside* of the container the container process must have the `CAP_SYS_ADMIN` capability (when specified in Kubernetes it's named `SYS_ADMIN`). Privileged containers will obey the `SET_HOSTNAME` variable and have a nice hostname:

```
[admin@opus /]# 
```

Unprivileged containers will get the default hostname which comes from Kubernetes: 

```
[admin@myserver-cloud-server-0 /]# 
```

There's no fix for this. 
