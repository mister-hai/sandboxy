    docker run -it --rm --name inetsim \
      -p 127.0.0.1:53:53/udp \
      -p 127.0.0.1:80:80 \
      -p 127.0.0.1:443:443 \
      -p 127.0.0.1:21:21 \
      -e INETSIM_START_SERVICES=dns,http,https,ftp \
      -e INETSIM_DNS_VERSION="DNS Version" \
      -e INETSIM_FTPS_BIND_PORT=21 \
      -v $(pwd)/user_configs:/opt/inetsim/conf/user_configs:ro \
      0x4d4c/inetsim

INetSim 1.2.7 (2017-10-22) by Matthias Eckert & Thomas Hungenberg

  Usage: /usr/bin/inetsim [options]

Available options:

    --help                         Print this help message.
    --version                      Show version information.
    --config=<filename>            Configuration file to use.
    --log-dir=<directory>          Directory logfiles are written to.
    --data-dir=<directory>         Directory containing service data.
    --report-dir=<directory>       Directory reports are written to.
    --bind-address=<IP address>    Default IP address to bind services to.
                                  Overrides configuration option 'default_bind_address'.
    --max-childs=<num>             Default maximum number of child processes per service.
                                  Overrides configuration option 'default_max_childs'.
    --user=<username>              Default user to run services.
                                  Overrides configuration option 'default_run_as_user'.
    --faketime-init-delta=<secs>   Initial faketime delta (seconds).
                                  Overrides configuration option 'faketime_init_delta'.
    --faketime-auto-delay=<secs>   Delay for auto incrementing faketime (seconds).
                                 Overrides configuration option 'faketime_auto_delay'.
    --faketime-auto-incr=<secs>    Delta for auto incrementing faketime (seconds).
                                  Overrides configuration option 'faketime_auto_increment'.
    --session=<id>                 Session id to use. Defaults to main process id.
    --pidfile=<filename>           Pid file to use. Defaults to '/var/run/inetsim.pid'.
