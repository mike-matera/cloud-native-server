FROM fedora:36 

RUN dnf install -y \
    systemd man openssh-server ansible git \
    @xfce-desktop tigervnc-server firefox \
    && dnf clean all 

COPY sshd.service /usr/lib/systemd/system/
RUN rm /usr/lib/systemd/system/sshd-keygen.target

RUN ln -fs multi-user.target /usr/lib/systemd/system/default.target

RUN mkdir /etc/rc.d &&  ln -s /etc/rc.local /etc/rc.d/rc.local

STOPSIGNAL SIGRTMIN+3
ENTRYPOINT ["/sbin/init"]
