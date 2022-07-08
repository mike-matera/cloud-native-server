# A Class' SSH Server in Kubernetes 

Since the dawn of the modern operating system, computer classes have used a shared login server to create a work environment for students. In the cloud era we've used virtual machines in place of physical servers (IaaS) to make our workloads more convenient to manage. But, our severs are still *pets*, they are precious to us, because they are stateful appliances running bespoke applications with some real problems: 

1. They are a single point of failure that impacts our ability to teach. 
1. Students are a security risk. I once caught a student who was able to maintain access after the end of a term. 
1. Management tools like VMware are clunky compared to cloud vendors. 
1. Cloud vendors are expensive for this kind of workload. 

This project is a way to deploy a traditional login server into a Kubernetes cluster. I started working on it as a way to get a deeper understanding of cloud-native computing.
 
## Quickstart 

You should have a Kubernetes cluster already built and `kubectl` and `helm` installed and configured. 

1. Check out this repo: 

    ```console
    $ git clone https://github.com/mike-matera/cloud-native-server.git
    $ cd cloud-native-server
    ```

2. Generate the SSH CA key: 

    ```console
    $ make
    ```

3. Create a file called `custom.yaml` with the following contents: 

    ```yaml
    rcEnv: |
        DEFAULT_USER="admin" 
        DEFAULT_KEY=""
        DEFAULT_KEY_IMPORT=""
        SET_HOSTNAME="myserver"
        CUSTOMIZE_REPO="https://github.com/mike-matera/cloud-native-server.git"
        CUSTOMIZE_CMD="ansible-playbook --connection=local --inventory 127.0.0.1, --limit 127.0.0.1 init/playbook.yaml"
    ```

    Update the `DEFAULT_KEY` variable to hold your SSH public key or the `DEFAULT_KEY_IMPORT` to a string suitable for [ssh-import-id](https://manpages.ubuntu.com/manpages/jammy/man1/ssh-import-id.1.html) to load public keys from your GitHub or Launchpad accounts. Update the `DEFAULT_USER` and `HOSTNAME` if you like. 

4. Use `helm` to deploy your server: 

    ```console 
    $ helm install test-ssh cloud-native-server/ --values custom.yaml --values secrets/ssh-keys.yaml
    ```

5. Wait for the application to deploy and check the service IP:

    ```console
    $ kubectl get service
    NAME                    TYPE           CLUSTER-IP       EXTERNAL-IP    PORT(S)        AGE
    test-ssh-cloud-server   LoadBalancer   10.152.183.173   172.20.2.100   22:31456/TCP   5s
    ```

    Login using the IP address:

    ```console
    $ ssh admin@172.20.2.100
    ```

## Configuration 

There are three configuration stages:

1. The `Dockerfile` build. The purpose of this stage is have a functional base container with most of good stuff installed. This is the least flexible stage. 
1. The execution of `rc.local` on boot. This stage customizes the image with SSH keys and creates the admin user. 
1. Executing an arbitrary command in an arbitrary GIT repository. This is the most flexible stage. 

The next sections describe how to customize each stage. 

### Custom Docker Images 

You can find the `Dockerfile` for the supported distros in the `containers` directory. If you clone this repository on GitHub you can reuse the `.github/workflows/*` files to build your own packages. Container builds are triggered by certain tags. For example, the Ubuntu container is build on a `jammy-*` tag. 

If you use a custom image add the following lines to your `custom.yaml` from the quickstart:

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
 
### Customizing Boot 

The images use `systemd` to run the classic `rc.local` script. This works well because there's existing infrastructure so not much image customization has to be done. The `sshd` service has been updated to wait for the `rc-local` service to finish, because SSH keys are generated by `/etc/rc.local`. The contents of `/etc/rc.local` are in the Helm chart. You can update the script by adding the following key to `custom.yaml`:

```yaml
rcLocal: |
  #! /usr/bin/bash
  set -e 

  . /etc/rc.env 
  
  [...your code here...]
```

You should look at the existing code in `cloud-native-server/values.yaml`. There are a few important things that the `rc.local` script must do: 

1. Set the hostname 
1. Create SSH host keys and sign them with the SSH CA key 
1. Create the admin user, make sure they have `sudo` access and install their SSH public keys 
1. Any personal customization 
1. Touch the `/ready` file to tell kubernetes that the container is ready. 

#### Why customize boot? 

1. If you have another way to deliver customization, i.e. Puppet or Chef networks.

### User Customization 

The default `rc.local` script looks for the existence of two variables that can be overridden using the `rcEnv` key in your `custom.yaml` file: 

```yaml
rcEnv: |
    DEFAULT_USER="admin" 
    DEFAULT_KEY=""
    DEFAULT_KEY_IMPORT=""
    SET_HOSTNAME="myserver"
    CUSTOMIZE_REPO="https://github.com/mike-matera/cloud-native-server.git"
    CUSTOMIZE_CMD="ansible-playbook --connection=local --inventory 127.0.0.1, --limit 127.0.0.1 init/playbook.yaml"
```

The `rc.local` script does the equivalent of: 

```bash 
git clone --recurse-submodules $CUSTOMIZE_REPO /tmp/repo-root
cd /tmp/repo-root 
$CUSTOMIZE_CMD
```

The commands are run as the user `$DEFAULT_USER`, not `root`. The variables from `rcEnv` are defined so you can add variables to `rcEnv` that are used by your custom repository command. The Ansible playbooks in `/init` are an example of how you can customize your systems.  

#### Why do user customization? 

1. This is the easiest way to customize your server. Try this first. 

## Security 

This project was inspired by running [LXD](https://linuxcontainers.org/lxd/introduction/) containers for the last few years. They took the place of VMware VMs and I was really happy with how much easier they are to build and manage. I started to wonder, *would it be possible to run `systemd` in an unprivileged container in Kubernetes?* It turns out the answer is no (I will explain this in detail at some point). This project runs `systemd` in a privileged container, but also supports unprivileged containers by launching `sshd` directly without `systemd`. 

Containerization is not a security technology. Running untrusted workloads --like a student shell-- carries a greater risk than running the same workload in a VM. But containers are lighter, more flexible and convenient, more robust and resilient than VMs. Until Kubernetes supports [user namespaces](https://kinvolk.io/blog/2020/12/improving-kubernetes-and-container-security-with-user-namespaces/) a container escape from a privileged container means the attacker has full control of the node. 

There is one essential question to consider when you deploy this project: 

> Will you give *untrusted* users `sudo` access? 

The next sections will show you how to configure the application based on the answer to the question above. 

### I Only Have Trusted `root` Users 

**Run the privileged version.** This the default. You can set the privileged setting in your `custom.yaml` file: 

```yaml
securityContext: 
  privileged: true
  capabilities:
    add:
      - SYS_ADMIN
```

This results in a very VM-like system. Users login and get a personal `cgroup` and can see each other with the `who` and `w` commands. The system runs normally with periodic security updates, `cron` and all of the things you'd expect. But, the container runs as root on the node so a container escape is serious. Container escapes are harder --maybe impossible-- as a non privileged user on your system. 

### I'm Giving Students `sudo` Access 

**Run the unprivileged version.**

```yaml
securityContext: 
  privileged: false
  capabilities: {}
```

This results in a system that's only running `sshd`. The Kubernetes deployment overrides the container's entrypoint do to this. Many things will still work and the user has `sudo` access. The container itself is running as an unprivileged user so a container escape is far less damaging. 

### The Hostname and `CAP_SYS_ADMIN` 

Annoyingly, in order to set the hostname *inside* of the container the container process must have the `CAP_SYS_ADMIN` capability (when specified in Kubernetes is just `SYS_ADMIN`). Containers that have the capability will obey the `SET_HOSTNAME` variable and have a nice hostname:

```
[admin@opus /]# 
```

Unprivileged containers will get the default hostname which comes from Kubernetes: 

```
[admin@fedora1-cloud-server-76b7cfd78-8tlw5 /]# 
```

There's no fix for this. 

### Don't Touch `allowPrivilegeEscalation`

The `allowPrivilegeEscalation` setting controls whether to obey the `suid` bit on programs in the container and must be set to `true`. While it may seem like a good way to restrain users, many programs on the system require `suid` to work, including `ping`, `sudo` and `passwd`. If you set `allowPrivilegeEscalation` to `false` those programs will fail. 