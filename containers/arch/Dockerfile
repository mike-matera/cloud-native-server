FROM docker.io/archlinux:latest as gcp_builder

ADD https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-397.0.0-linux-x86_64.tar.gz /
RUN tar -xvf google-cloud-cli-397.0.0-linux-x86_64.tar.gz

FROM docker.io/archlinux:latest 

RUN rm /usr/lib/systemd/system/systemd-firstboot.service

RUN pacman -Sy && pacman -S --noconfirm openssh \
    ansible python-pip man-db man-pages zsh ksh tcsh podman xfce4 tigervnc \
    terraform vim git firefox

COPY --from=gcp_builder /google-cloud-sdk /opt/google-cloud-sdk

RUN mkdir -p /etc/ssh/ca

STOPSIGNAL SIGRTMIN+3
ENTRYPOINT ["/sbin/init"]
