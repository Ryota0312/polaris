[Unit]
Description=Create virtual folder system.

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'exec APPLICATION_ROOT/run.sh'