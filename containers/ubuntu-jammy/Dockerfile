FROM scratch 

ADD jammy-server-cloudimg-amd64-root.tar.xz / 
RUN rm /etc/systemd/system/network-online.target.wants/systemd-networkd-wait-online.service \
    && rm /etc/systemd/system/multi-user.target.wants/systemd-resolved.service \
    && rm /lib/systemd/system/systemd-resolved.service \
    && rm /etc/resolv.conf \
    && rm /etc/systemd/system/multi-user.target.wants/snapd.* \
    && rm /etc/systemd/system/multi-user.target.wants/ModemManager.service \ 
    && rm /etc/systemd/system/multi-user.target.wants/networkd-dispatcher.service 

COPY mozilla-firefox-pin /etc/apt/preferences.d/mozilla-firefox
RUN apt update -y && DEBIAN_FRONTEND=noninteractive apt install -y \
    curl git ansible xfce4 xfce4-goodies tightvncserver firefox \
    python3-pip tree bsdmainutils dictionaries-common wamerican \
    mtr zsh ksh tcsh csh podman ubuntu-server \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /etc/ssh/ca

STOPSIGNAL SIGRTMIN+3
ENTRYPOINT ["/sbin/init"]
