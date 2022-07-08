# A Class' SSH Server in Kubernetes 

Since the dawn of the modern operating system, computer classes have used a shared login server to create a work environment for students. In the cloud era we've used virtual machines in place of physical servers (IaaS) to make our workloads more convenient to manage. But, our severs are still *pets*, they are precious to us, because they are stateful appliances running bespoke applications with some real problems: 

1. They are a single point of failure that impacts our ability to teach. 
1. Students are a security risk. A student was once able to maintain access after the end of a term. 
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
    $ helm install test-ssh chart --values custom.yaml --values secrets/ssh-keys.yaml
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

This is a work in progress! 


