[comment]: #

# Archiving system for Nextcloud

## Installation and setup

1. `cd ~ && git clone https://github.com/Muzosh/archiving-system-nextcloud.git`
1. install python3 (any version should be fine, 3.10.2 works 100%) and PyPI (pip)
1. (optional for development) create virtual environment and activate it
1. install archivingsystem with dependencies:
    > sudo pip install \<path-to-this-project\>
    - SUDO IS IMPORTANT (it will install it globally, so php engine can access it)
1. (optional) install linter, formatter, etc. used for this project
    > sudo pip install flake8 black rope bandit
1. download, install and setup RabbitMQ

    - install via _./docs/rabbimq_setup.sh_ installation script
    - run commands:

    ```bash
    sudo rabbitmq-plugins enable rabbitmq_management

    sudo rabbitmqctl add_user "ncadmin" # (password "ncadmin")

    sudo rabbitmqctl add_vhost archivingsystem

    sudo rabbitmqctl set_permissions -p "archivingsystem" "ncadmin" ".*" ".*" ".*"

    sudo rabbitmqctl set_user_tags ncadmin administrator
    ```

    - create queues (archivingsystem vhost, everything else default) in management console (`http://{node-hostname}:15672/`): `archiving`, `failed_tasks`, `validation`, `retimestamping`, `archiving_system_logging`

1. create new exchange:
    - `virtual host = archivingsystem`
    - `name = log`
    - `type = topic`
    - else default
1. after that, open newly created exchange and add binding
    - `to_queue = archiving_system_logging`
    - `routing_key = archiving_system_logging.*`
1. create mysql tables
    - `sudo mysql -v -uroot -p < path-to-sql-file`
    - scripts are available in ./data/sqlscripts, run then one by one
1. initialise "Workflow external scripts"
    - install application from source code
        - `sudo cp -r data/workflow_script /var/www/nextcloud/apps` (this command includes all hidden files)
        - `sudo chown -R www-data:www-data /var/www/nextcloud/apps/workflow_script`
    - enable the app using the OCC Nextcloud console app
        - `occ app:enable workflow_script`
1. change Workflow external script setting
   - in Nextcloud web interface go to settings -> Administration -> Flow -> Run script and add new Flow:
       - When: Tag assigned
       - and: File system tag - is tagged with - "archive" (need to create this tag on some dummy file first)
       - script to run: `sh /home/nextcloudadmin/archiving-system-nextcloud/bin/nc_archive_file.sh %p %o`
   - setup Cron
       - in Nextcloud web interface go to settings -> Administration -> Basic settings -> Background jobs: select Cron
       - `sudo crontab -u www-data -e` -> select some editor, nano for example
       - on last line add `*  *  *  *  * php -f /var/www/nextcloud/cron.php`
       - verify by `sudo crontab -u www-data -l`
1. generate and obtain certificates
   - `mkdir ~/certs`
   - generate self-signed certificate:
       - `sudo openssl req -newkey rsa:4096 -x509 -sha256 -days 365 -out ~/certs/myCert.crt -keyout ~/certs/myCert.key`
       - chosen passphrase will be used in config (default: "cert_pass")
   - generate TSA files:
       - `wget https://freetsa.org/files/tsa.crt -O ~/certs/tsa.crt`
       - `wget https://freetsa.org/files/cacert.pem -O ~/certs/cacert.pem`
1. finish config
   - go through all files in `config` folder and check configuration (create necessary folders for example)
   - check file `bin/nc_archive_file.sh` and input correct python path
1. try to run and debug all tests in `tests`
    - some of them might need some tweaks (like changing FileID etc.)
    - use some database management tool to also view records in `archivingsystem` database

## TODO How to execute

- all executable scripts are in _./bin_ folder
    - .py must be executed with python interpreter and appropriate config file path from _./config_ must be set as parameter
- there is usage print when you run script without correct parameters

Outdated:

- if you are planning to run archiving and validation worker remotly from file storage:
    - setup sftp connection - create keys etc...
    - setup login only using keys
    - setup proper data to configs
    - ensure that user which is used for remote login has access rigths to given directories

### Config formats

- Inside all config examples are comments explaining different fields
- All workers have defined their own configs
- db_config part can be formated by this -> <https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html>

### (Outdated) Task Scripts

| name                     | purpose                                                                                                                           |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| make_archiving_task.py | Manual creation of task for archiving of given file                                                                             |
| retimestamping_task.py   | Regular checking of timestamps expiration dates in database and creating a task for those which validity is ending within 24 ours |
| validation_task.py       | Interactive interface for creating tasks for validation of archived files                                                         |

### (Outdated) Workers

| name                     | purpose                                                   |
| ------------------------ | --------------------------------------------------------- |
| archiving_worker.py    | responsible for consuming archiving tasks from rabbitmq |
| retimestamping_worker.py | responsible for consuming tasks for retimestamping        |
| validation_worker.py     | responsible for validation of archived files              |
