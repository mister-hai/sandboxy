## nginx_template.conf

    gets copied to 
        /containers/nginx/nginx.conf.template

    AFTER you modify it, this allows linters to format it properly
    There is probably a better solution

    Add entries in the conf to reflect the app you wish to proxy to

## config.ini

    This gets copied to
        /containers/ctfd/config.ini

    Set the values to reflect your environment


    https://github.com/wmnnd/nginx-certbot