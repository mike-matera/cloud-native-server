FROM fedora:36 

RUN dnf install -y \
    systemd man openssh-server ansible \
    @xfce-desktop-environment tigervnc-server firefox \
    && dnf clean all 

COPY sshd.service /usr/lib/systemd/system/
RUN rm /usr/lib/systemd/system/sshd-keygen.target

STOPSIGNAL SIGRTMIN+3
ENTRYPOINT ["/sbin/init"]
