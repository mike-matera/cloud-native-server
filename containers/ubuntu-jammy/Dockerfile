FROM scratch 

ADD jammy-server-cloudimg-amd64-root.tar.xz / 
RUN rm /etc/systemd/system/network-online.target.wants/systemd-networkd-wait-online.service \
    && rm /etc/systemd/system/multi-user.target.wants/systemd-resolved.service \
    && rm /lib/systemd/system/systemd-resolved.service \
    && rm /etc/resolv.conf \
    && rm /etc/systemd/system/multi-user.target.wants/snapd.* \
    && rm /etc/systemd/system/multi-user.target.wants/networkd-dispatcher.service 

COPY mozilla-firefox-pin /etc/apt/preferences.d/mozilla-firefox
RUN apt update -y && DEBIAN_FRONTEND=noninteractive apt install -y \
    curl git ansible xfce4 xfce4-goodies tightvncserver firefox \
    python3-pip python3-venv tree bsdmainutils dictionaries-common wamerican \
    mtr zsh ksh tcsh csh podman ubuntu-server aspell \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Google Cloud SDK
RUN apt-get install -y apt-transport-https ca-certificates gnupg \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - \
    && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && apt-get update -y && apt-get install -y google-cloud-sdk

# Install Terraform
RUN curl -fsSL https://apt.releases.hashicorp.com/gpg | apt-key add - \
    && apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
    && apt-get update -y && DEBIAN_FRONTEND=noninteractive apt-get install -y terraform

RUN mkdir -p /etc/ssh/ca

STOPSIGNAL SIGRTMIN+3
ENTRYPOINT ["/sbin/init"]
