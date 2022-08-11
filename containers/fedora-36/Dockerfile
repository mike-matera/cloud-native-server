FROM fedora:36 

# Re-install man pages
COPY dnf.conf /etc/dnf/dnf.conf 
RUN dnf reinstall -y $(dnf list --installed | cut -d' ' -f1)

RUN dnf install -y \
    systemd man man-pages man-db openssh-server ansible git \
    @xfce-desktop tigervnc-server firefox zsh ksh tcsh csh \
    podman \
    && dnf clean all 

# Install Terraform 
RUN dnf install -y dnf-plugins-core \
    && dnf config-manager --add-repo https://rpm.releases.hashicorp.com/fedora/hashicorp.repo \
    && dnf install -y terraform

# Install gcloud 
COPY google-cloud-sdk.repo /etc/yum.repos.d/google-cloud-sdk.repo
RUN dnf install -y libxcrypt-compat.x86_64 google-cloud-cli

RUN ln -fs multi-user.target /usr/lib/systemd/system/default.target

RUN mkdir -p /etc/rc.d &&  ln -s /etc/rc.local /etc/rc.d/rc.local

STOPSIGNAL SIGRTMIN+3
ENTRYPOINT ["/sbin/init"]
