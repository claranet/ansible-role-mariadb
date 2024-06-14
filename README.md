# Ansible role - mariadb
[![Maintainer](https://img.shields.io/badge/maintained%20by-claranet-e00000?style=flat-square)](https://www.claranet.fr/)
[![License](https://img.shields.io/github/license/claranet/ansible-role-mariadb?style=flat-square)](LICENSE)
[![Release](https://img.shields.io/github/v/release/claranet/ansible-role-mariadb?style=flat-square)](https://github.com/claranet/ansible-role-mariadb/releases)
[![Status](https://img.shields.io/github/actions/workflow/status/claranet/ansible-role-mariadb/molecule.yml?branch=main&style=flat-square&label=tests)](https://github.com/claranet/ansible-role-mariadb/actions?query=workflow%3A%22Ansible+Molecule%22)
[![Ansible version](https://img.shields.io/badge/ansible-%3E%3D2.10-black.svg?style=flat-square&logo=ansible)](https://github.com/ansible/ansible)
[![Ansible Galaxy](https://img.shields.io/badge/ansible-galaxy-black.svg?style=flat-square&logo=ansible)](https://galaxy.ansible.com/claranet/mariadb)


> :star: Star us on GitHub — it motivates us a lot!

Install and configure MariaDB server on Debian,Redhat systems

## :warning: Requirements

Ansible >= 2.10

## :arrows_counterclockwise: Dependencies
```yaml
- community.mysql.mysql_db
- community.mysql.mysql_user
- community.mysql.mysql_replication
```

## :zap: Installation

```bash
ansible-galaxy install claranet.mariadb
```

### MariaDB version to be installed 
----
_default is 10.11_
```yaml
mariadb_version: '10.11'
```
### Available features and tags
-----
This role support the following features and tags in the following order during execution:
Feature                 | Tag
------------------------|---------------------
Installation            | install
Data at rest encryption | encryption
Configuration           | configure
Secure installation     | secure-installation
User management         | users
Replication             | replication
Database management     | databases
Backup                  | backup

### Proxy usage
----
This role supports use of proxies.

The variables `mariadb_http_general_proxy` and `mariadb_https_general_proxy` can be used to specify a proxy for general internet access (such as downloading files).

The variables `mariadb_http_pkg_proxy` and `mariadb_https_pkg_proxy` can be used to specify a proxy for package manager interaction (such as downloading packages or updating cache).

Note: These variables are translated to environnement variables http_proxy and https_proxy which are passed to corresponding tasks.

### Create/Remove database users
----
This value controls on which host users with neither host nor hosts keys are specified
_default is localhost_
```yaml
mariadb_users_default_host: localhost
```

_Passwords are required!_
```yaml
mariadb_users_default_host: localhost
mariadb_users:
  - name: 'user1' # neither host or hosts key is specified so user1 will be created with the value of the variable mariadb_users_default_host
    password: '*******'
    priv: '*.*:USAGE'
    home: /home/example  # Assumes this directory already exists on the remote server
    copy_cnf: true
    state: present

  - name: 'user1' # host key is specified so user2 will be created with the specified value
    password: '*******'
    priv: '*.*:USAGE'
    host: 127.0.0.1

  - name: 'user3' # hosts keys is specified so user3 will be created with every single one of the  values
    state: absent
    hosts:
      - ::1
      - 127.0.0.1
      - localhost:
      - 10.10.10.3
      
  - name: 'old'
    state: absent
    host: localhost
```
When dealing with replication, the role only configures users on the primary server and replication is expected to carry the users configuration to the replica nodes.

### Setting user privileges on databases and tables
----

Define user privileges per the following format:
```
db.table:priv1,priv2
```

Idempotent solution for multiple priviledges (@see http://stackoverflow.com/a/22959760)

```yaml
mariadb_privileges:
  - db1.*:ALL,GRANT
  - db2.*:USAGE
  
mariadb_users:  
  - name: 'user1'
    password: 'travis'
    priv: "{{ mariadb_privileges|join('/') }}"
```

### Create/Remove databases
----

All databases need to be defined in `mariadb_databases`:

```yaml
mariadb_databases:
  - name: 'testdb'
    collation: utf8_general_ci
    encoding: utf8
    state: present

  - name: 'olddb'
    state: absent
```
#### Excluding databases from replication
When managing replication, it's recommended to selectively exclude databases from replication by setting `replicate: false` for the corresponding entry in `mariadb_databases`.

#### Restricting replication to certain databases
You can do so by setting `replicate: true` on the corresponding entries but this means replication will focus solely on changes to those specific databases. Therefore, certain essential features like `user (mysql.user)` replication might not work.

### Master/Slave Replication
----

Configuration example for master :

```yaml
---
- hosts: mariadb01
  become: true
  become_method: sudo
  vars:
    mariadb_server_id: 1
    mariadb_replication_role: 'primary'
    mariadb_replication_username: 'replicationuser'
    mariadb_replication_password: 'myPassword'
    mariadb_admin_user: "admin"
    mariadb_admin_password:  "myAdminPassword"
  roles:
    - role: claranet.mariadb
      tags: ["install,secure-installation,configure,replication"]
```

Configuration example for slave :

```yaml
---
- hosts: mariadb02
  become: true
  become_method: sudo
  vars:
    mariadb_server_id: 2
    mariadb_replication_role: 'replica'
    mariadb_replication_primary: 'mariadb01' # a name the slave can use to connect to the master server
    mariadb_replication_username: 'replicationuser'
    mariadb_replication_password: 'myPassword'
    mariadb_admin_user: "admin"
    mariadb_admin_password:  "myAdminPassword"
  roles:
    - role: claranet.mariadb
      tags: ["install,secure-installation,configure,replication"]
```

Notes
------
If for some reason the hostname used by the ansible controller node to communicate with the replication master node is different that the value provided in `mariadb_replication_primary`, you can set the variable `mariadb_replication_primary_inventory_host` to that value.


Encryption at rest
------------------
Enable [Data Encryption At Rest](https://mariadb.com/kb/en/securing-mariadb-data-at-rest-encryption/).  
This tasks use [File Key Management Encryption Plugin](https://mariadb.com/kb/en/file-key-management-encryption-plugin/) to enable the MariaDB's data-at-rest encryption.  


The following example will set up automatically 5 encryption keys with a randomly generated encryption password stored in a file named with the variable `mariadb_file_key_management_filekey`.
```yaml
---
- hosts: mariadb02
  become: true
  become_method: sudo
  vars:
    mariadb_data_at_rest_encryption: true
    mariadb_encryption_keygen_auto: true
    mariadb_encryption_keygen_count: 5
    mariadb_innodb_encrypt_tables: 'ON'
    mariadb_innodb_encrypt_temporary_tables: 'ON'
    mariadb_innodb_encrypt_log: 'ON'
    mariadb_encrypt_binlog: 'ON'
    mariadb_aria_encrypt_tables: 'ON'
    mariadb_encrypt_tmp_disk_tables: 1
    mariadb_encrypt_tmp_files: 1
    mariadb_admin_password: root
  roles:
    - role: claranet.mariadb
      tags: ["install,secure-installation,configure,encryption"]
```



In the following example, keys are directly filled in the playbook but Ansible Vault can be used to retrieve the encryption keys too as long as each resulting key fits on a single line everything should be fine.


```yaml
---
- hosts: mariadb02
  become: true
  become_method: sudo
  vars:
    mariadb_data_at_rest_encryption: true
    mariadb_encryption_keygen_auto: false
    mariadb_innodb_encrypt_tables: 'ON'
    mariadb_innodb_encrypt_temporary_tables: 'ON'
    mariadb_innodb_encrypt_log: 'ON'
    mariadb_encrypt_binlog: 'ON'
    mariadb_aria_encrypt_tables: 'ON'
    mariadb_encrypt_tmp_disk_tables: 1
    mariadb_encrypt_tmp_files: 1
    mariadb_encryption_keys:
      1: "b326176e96aef8fa324c130835b1496031cf7838f4a17c70046997996103f651"
      2: "3c32960d4194cb2b4850144880d209e500b85bd73d7935ad9734cad6dc7a8948"
      3: "6f8642ee71fca20f3ffc9819f64e2424786ede63eb9bea4b56f4db1473d150ad"
    mariadb_encryption_password: "913b847d83a8049a09f53b89bdde1465086c8b4c970a09cb91d75b2db1384e42ccc872ae996bf7cbe8f8f9ecea74795607471591565c1215a064c5c2e7fa698a9f80df668a3436587dfa8edc7a74254eee37a131de31fd0279ff5cd945655b7662d1523673c37d19546c27c83776ad3c87416a472e4c1c79fffa0c2dce462af1"
    mariadb_innodb_default_encryption_key_id: 10
    mariadb_admin_password: root
  roles:
    - role: claranet.mariadb
      tags: ["install,secure-installation,configure,encryption"]
```

Notes :
-------
* The MariaDB's data-at-rest encryption need "mariadb_overwrite_global_mycnf: true", the default.  
* The MariaDB's data-at-rest encryption must be setup before encrypting any tables.
* The MariaDB's data-at-rest encryption is a table option set when it's [created](https://mariadb.com/kb/en/file-key-management-encryption-plugin/#using-the-file-key-management-plugin).
* The MariaDB's data-at-rest encryption is replication compatible.

If you want to manually create the encryption keys and the password used for encryption, you can run the following commands :
```bash
$ openssl rand -hex 32  # for each encryption key
$ openssl rand -hex 128 # for the encryption password
```

### Advanced customized installation
----
There is a variable `mariadb_repo_template_path` that contains the path to a template file used to generate the repository file generate onto the server. The generated repository file contains the mirrors, mariadb version and dictates the installation. 

Therefore if this variable is overriden `mariadb_repo_template_path: path/relative/to/playbook/custom_repofile` with a custom file you then have the complete control over which version and from where mariadb will be installed.

#### Main and extra configuration location
By default, this role generates the MySQL configuration file and outputs it to a file named `99-ansible-role-mariadb-my.cnf`. This file is placed within one of the extra configuration directories included in the default `my.cnf` file. The specific path of this configuration file is determined by the variable `mariadb_config_file`.

We recommend keeping the default value for `mariadb_config_file` as it ensures that the configuration from this role persists during system upgrades, which may reset the default `my.cnf`. Using a different file for the configuration ensures that changes made by this role will be preserved across upgrades.

On Debian systems, the main configuration file (value of `mariadb_config_file`) is stored at `/etc/mysql/mariadb.conf.d/99-ansible-role-mariadb-my.cnf`, while on RedHat systems, it is located at `/etc/my.cnf.d/99-ansible-role-mariadb-my.cnf`.

If you switch the value of `mariadb_config_file` to the default `my.cnf` path, the default extra configuration directories are not included by default. You can change that behaviour by setting the variable `mariadb_config_include_default_dirs` to `true`. Be very cautious while doing this as some *cnf* files might already be present in those default directories and including them might alter the final configuration in unpredictable ways.

If you wish to add some custom configuration, you can do so by setting the variable `mariadb_config_include_dir` to a directory that will hold all your extra configuraton files. Fill the variable `mariadb_config_include_files` with the actual configuration files as per the documentation.
Ensure that your extra configuration files have the highest priority to prevent them from being overridden, especially when the chosen directory is not empty.


## :pencil2: Full Example Playbook

```yaml
---
- hosts: all
  roles:
    - role: claranet.mariadb
      tags: [always,install,encryption,configure,secure-installation,replication,databases,users,backup]
      vars:
        mariadb_debug: true
        mariadb_version: "10.11"
        mariadb_admin_password: root

        mariadb_replication_role: master
        mariadb_replication_username: replic
        mariadb_replication_password: replic
        # IP addresses of the two replicas that will connect to this primary server
        # If you want to use dns names for hosts, remember to set mariadb_skip_name_resolve to false
        mariadb_replication_hosts: ["172.17.0.1", "172.17.0.2", "localhost"]

        mariadb_databases:
          - name: db1
          - name: db2
            replicate: true
          - name: db3 # Only db3 will not replicate
            replicate: false
            encoding: utf8
            collation: utf8_general_ci
            state: present

        mariadb_users_default_host: localhost
        mariadb_users:
          - name: user1
            password: strong password1
          - name: user2
            password: strong password2
            hosts:
              - ::1
              - 127.0.0.1
              - 172.17.0.1
          - name: user3
            password: strong password3
            host: '%'

        mariadb_data_at_rest_encryption: true
        mariadb_encryption_keygen_auto: false
        mariadb_innodb_encrypt_tables: 'ON'
        mariadb_innodb_encrypt_temporary_tables: 'ON'
        mariadb_innodb_encrypt_log: 'ON'
        mariadb_encrypt_binlog: 'ON'
        mariadb_aria_encrypt_tables: 'ON'
        mariadb_encrypt_tmp_disk_tables: 1
        mariadb_encrypt_tmp_files: 1
        mariadb_encryption_keys:
          1: "b326176e96aef8fa324c130835b1496031cf7838f4a17c70046997996103f651"
          2: "3c32960d4194cb2b4850144880d209e500b85bd73d7935ad9734cad6dc7a8948"
          3: "6f8642ee71fca20f3ffc9819f64e2424786ede63eb9bea4b56f4db1473d150ad"
        mariadb_encryption_password: "913b847d83a8049a09f53b89bdde1465086c8b4c970a09cb91d75b2db1384e42ccc872ae996bf7cbe8f8f9ecea74795607471591565c1215a064c5c2e7fa698a9f80df668a3436587dfa8edc7a74254eee37a131de31fd0279ff5cd945655b7662d1523673c37d19546c27c83776ad3c87416a472e4c1c79fffa0c2dce462af1"
        mariadb_innodb_default_encryption_key_id: 10

        mariadb_backup_mail_addr: admin@fakemail.com
        mariadb_backup_keep_count: 3
        mariadb_backup_schedule:
          hour: 3
          minute: 0

        mariadb_systemd_override_dir: /etc/systemd/system/mariadb.service.d
        mariadb_systemd_override:
          - filename: 10-limitcore.conf
            section: Service
            options:
              LimitNOFILE: 100000
              LimitMEMLOCK: 100000
```


Linux/MariaDB versions supported
-----

Linux/MariaDB     | 10.3 | 10.4 | 10.5 | 10.6 | 10.11
------------------|:----:|:----:|:----:|:----:|:------: 
Debian 10         | Yes  | Yes  | Yes  | Yes |  Yes
Debian 11         | No   | No   | Yes  | Yes |  Yes
Debian 12         | No   | No   | No   | No  |  Yes
Ubuntu 20.04,18.04| Yes  | Yes  | Yes  | Yes |  Yes
Ubuntu 22.04      | No   | No   | No   | Yes |  Yes
CentOS 8          | Yes  | Yes  | Yes  | Yes |  Yes
Fedora 37         | No   | No   | No   | Yes |  Yes


## :gear: Role variables
 Outer pipes Cell padding

Variable name                              | Default value                           | Notes                                                                                                        |
------------------------------------------ |-----------------------------------------|--------------------------------------------------------------------------------------------------------------|
mariadb_version                            | "10.11"                                  |
mariadb_debug                              | false                                   | Controls wether or not to show debug infos. Activating this will potentially make ansible some mariadb credentials                                                                                                                                                                                         |
mariadb_mirror_base_url                    | null                                    | The url base used in conjunction with the distro type, mariadb version during the generation of the repository config file. OS dependent                                                                                                                                                                |
mariadb_repo_template_path                 | null                                    | Repository template file templated out to the server before installing. OS dependent. this file controls entirely which version of mariadb is installed. Therefore, overriding this template file with a custom one will entirely bypass mariadb_version, and mariadb_mirror_base_url variables              |
mariadb_manage_pip_dependencies                 | true                                    | Whether or not to run pip related task (can be usefull for users who want to install mysql driver libraries through other means)              |
mariadb_packages_extra                 | []                                    | Extra packages to install with mariadb              |
mariadb_http_general_proxy                 | null                                    | HTTP proxy to use for general internet access on the MariaDB server                                                                                                                                                                                              |
mariadb_https_general_proxy                | null                                    | HTTPS proxy to use for general internet access on the MariaDB server                                                                                                                                                                                              |
mariadb_http_pkg_proxy                     | null                                    | HTTP proxy to use for package manager interaction (such as downloading packages, updating cache, etc) on the MariaDB server                                                                                                                                                                                      |
mariadb_https_pkg_proxy                    | null                                    | HTTPS proxy to use for package manager interaction (such as downloading packages, updating cache, etc) on the MariaDB server                                                                                                                                                                                      |
mariadb_admin_home                         | '/root'                                 | Linux home of the mariadb admin user                                                                         |
mariadb_admin_user                         | 'root'                                  | Name of the admin user inside the mariadb dbms                                                               |
mariadb_admin_password                     | ''                                      | Mariadb admin user password                                                                                  |
mariadb_admin_force_password_update        | true                                    | Update the admin password ?                                                                                  |
mariadb_overwrite_global_mycnf             | true                                    | Overwrite MariaDB main configuration file my.cnf on every ansible run                                        |
mariadb_config_include_dir                 | null                                    | Directory path for additional mariadb configuration on your system. OS depdendent, default on Debian systems is /etc/mysql/mariadb.conf.d and on RedHat is /etc/my.cnf.d                            |
mariadb_config_include_files               | []                                      | List of additionnal configuration files to copy to the server. Each element has the format  `{ src: path/relative/to/playbook/file.cnf, force: true }`                                                                                                                                                        |
mariadb_config_include_default_dirs        | false                                    | Controls whether or not to include the default extra configuration directories in the `mariadb_config_file` points to the default `my.cnf` path
mariadb_enabled_on_startup                 | true                                    | Enable mariadb service on startup ?                                                                          |
mariadb_users_default_host                 | localhost                               | The default host assigned to new users if no hosts is defined                                                |
mariadb_users                              | []                                      | List used to manage users on the mariadb server                                                              |
mariadb_databases                          | []                                      | List used to managed databases on the mariadb server                                                         |
mariadb_error_log_enabled                  | true                                    |
mariadb_slow_query_log_enabled             | true                                    |
mariadb_replication_role                   | ''                                      | primary/replica master/slave                                                                                 |
mariadb_replication_primary                | ''                                      | Primary hostname used to configure the replica servers                                                       |
mariadb_replication_primary_inventory_host | "{{ mariadb_replication_primary }}"     | A name the ansible controller can use to connect to the primary server                                       |
mariadb_replication_primary_socket         | "{{ \_mariadb_socket  }}"               | The socket of mariadb service on the primary server                                                          |
mariadb_replication_username               | 'replic'                                | Username of the replication user to be created on the primary server                                         |
mariadb_replication_password               | ''                                      | Password of the replication user                                                                             |
mariadb_replication_priv                   | '*.*:REPLICATION SLAVE'                 | Privileges of the replication user                                                                           |
mariadb_replication_hosts                  | ['%']                                   | List of hosts to create the replication user with. This can be used to restrict the user to only the replicas servers address                                                                                                                                                                                     |
mariadb_data_at_rest_encryption            | false                                   |
mariadb_encryption_keygen_auto             | true                                    | When true, mariadb_encryption_keys and mariadb_encryption_password are automatically generated               |
mariadb_encryption_keygen_count            | 3                                       | The number of encryption keys to generate if mariadb_encryption_keygen_auto is true                          |
mariadb_encryption_keys                    | ""                                      | Dictionnary version of the encryption keys                                                                   |
mariadb_encryption_password                | ''                                      | Password used to encrypt the encryption keys                                                                 |
mariadb_key_management_plugin              | file_key_management                     | This variable is translated to a plugin_load_add= value in the my.cnf configuration file in order to load the encryption plugin                                                                                                                                                                                   |
mariadb_file_key_management_override       | false                                   | Controls wether encrypted keys and password should be overiden or only created if the corresponding two files don't exist yet                                                                                                                                                                                     |
mariadb_file_key_management_dir            | /etc/mysql/encryption                   | Directory holding encryption related files                                                                   |
mariadb_systemd_override_dir               | /etc/systemd/system/mariadb.service.d   | Mariadb service override variables                                                                           |
mariadb_systemd_override                   |                                         | The options per entry are translated to a file with the corresponding name in mariadb_systemd_override_dir folder in ini format and under a section with the given name. Refer to examples in this readme for the expected format                                                                              |
mariadb_backup                    | true                                | Whether or not to run backup tasks (will not remove backup if already planned)  |
mariadb_backup_root_dir                    | /backups                                | Root directory containing the backups                                                                        |
mariadb_backup_dbnames                     | "all"                                   | Databases to backup or all to backup all databases                                                           |
mariadb_backup_dbexclude                   | "information_schema performance_schema" | Databases to not backup. You can append more databases here. Be carefull not to remove the original ones in the list otherwise errors might occur during backup execution                                                                                                                                       |
mariadb_backup_cron_job_name               | MariaDB - Backup management             | The name of the cron job created to run the backup job on a recurring basis                                  |
mariadb_backup_schedule                    | {minute: 0, hour: 0}                    |
mariadb_backup_keep_count                  | 8                                       | Maximum age in days that backups are kept before deleted                                                     |
mariadb_backup_mail_addr                   | admin@email.com                         | An email address that will be notified after each backup execution                                           |


Buy Me a Coffee at ko-fi.com

MySQL configuration variables
----
The following variables are defined and correspond to their respective mysql configuration variable used in `my.cnf` file without the prefix `mariadb_` .

Variable name                                    | Default value                     | Notes                                                                                                        |
------------------------------------------------ |---------------------------------- |------------------------------------------------------------------------------------------------------------- |
mariadb_port                                     | "3306"                            |
mariadb_bind_address                             | '0.0.0.0'                         |
mariadb_datadir                                  | "/var/lib/mysql"                  |
mariadb_pid_file                                 | null                              | Default value is OS dependent. on debian is= '/var/run/mysqld/mysqld.pid', on redhat is '/var/lib/mysql/mariadb.pid'                                     |
mariadb_socket                                   | null                              | Default value is OS dependent. on debian is= '/var/run/mysqld/mysqld.sock', on redhat is '/var/lib/mysql/mysql.sock'                                      |
mariadb_key_buffer_size                          | "256M"                            |
mariadb_max_allowed_packet                       | "128M"                            |
mariadb_table_open_cache                         | "256"                             |
mariadb_sort_buffer_size                         | "1M"                              |
mariadb_read_buffer_size                         | "1M"                              |
mariadb_read_rnd_buffer_size                     | "4M"                              |
mariadb_myisam_sort_buffer_size                  | "64M"                             |
mariadb_table_cache                              | 2000                              |
mariadb_thread_cache_size                        | "8"                               |
mariadb_query_cache_size                         | "16M"                             |
mariadb_max_connections                          | 151                               |
mariadb_tmp_table_size                           | '64M'                             |
mariadb_max_heap_table_size                      | '64M'                             |
mariadb_join_buffer_size                         | '3M'                              |
mariadb_innodb_file_per_table                    | "1"                               |
mariadb_innodb_buffer_pool_size                  | "256M"                            |
mariadb_innodb_log_file_size                     | "64M"                             |
mariadb_innodb_log_buffer_size                   | "8M"                              |
mariadb_innodb_flush_log_at_trx_commit           | "2"                               |
mariadb_innodb_lock_wait_timeout                 | 600                               |
mariadb_innodb_additional_mem_pool_size          | "8M"                              |
mariadb_mysqldump_max_allowed_packet             | "64M"                             | Corresponds to max_allowed_packet attribute under mysqldump section in the configuration file                                             |
mariadb_log                                      | ""                                |
mariadb_log_error                                | "/var/log/mariadb/mysql.err"      |
mariadb_syslog_tag                               | null                              | Default value is OS dependent. on debian is= 'mysql', on redhat is 'mariadb'                                 |
mariadb_slow_query_log_file                      | "/var/log/mariadb/mysql-slow.log" |
mariadb_slow_query_time                          | 2                                 |
mariadb_server_id                                | "1"                               |
mariadb_max_binlog_size                          | "100M"                            |
mariadb_expire_logs_days                         | "10"                              |
mariadb_innodb_encrypt_tables                    | 'OFF'                             |
mariadb_innodb_encrypt_temporary_tables          | 'OFF'                             |
mariadb_innodb_encrypt_log                       | 'OFF'                             |
mariadb_innodb_encryption_threads                | 4                                 |
mariadb_innodb_encryption_rotate_key_age         | 0                                 |
mariadb_innodb_default_encryption_key_id         | 1                                 |
mariadb_encrypt_tmp_disk_tables                  | 0                                 |
mariadb_encrypt_tmp_files                        | 0                                 |
mariadb_encrypt_binlog                           | 'OFF'                             |
mariadb_aria_encrypt_tables                      | 'OFF'                             |
mariadb_file_key_management_filekey              | password_file                     | This variable while being translated inside the configuration file is prepended with {{ mariadb_file_key_management_dir }}/              |
mariadb_file_key_management_filename             | keys.enc                          | This variable while being translated inside the configuration file is prepended with {{ mariadb_file_key_management_dir }}/              |
mariadb_file_key_management_encryption_algorithm | 'AES_CBC'                         |
mariadb_wait_timeout                             | 1800                              |
mariadb_net_read_timeout                         | 120                               |
mariadb_skip_name_resolve                        | true                              |
mariadb_back_log                                 | 100                               |
mariadb_max_connect_errors                       | 10000                             |
mariadb_open_files_limit                         | 20000                             |
mariadb_interactive_timeout                      | 3600                              |
mariadb_connect_timeout                          | 120                               |

## :closed_lock_with_key: [Hardening](HARDENING.md)

## :heart_eyes_cat: [Contributing](CONTRIBUTING.md)
Checkout the [Contributing](CONTRIBUTING.md) if you are looking for a guide on how to setup an environnement so you can test this role as a developper.


## :copyright: [License](LICENSE)

[Mozilla Public License Version 2.0](https://www.mozilla.org/en-US/MPL/2.0/)

## Author information

Proudly made by the Claranet team and inspired by:
- [Tobias Schifftner](https://github.com/tschifftner/ansible-role-mariadb)
- [Jeff Geerling](https://github.com/geerlingguy/ansible-role-mysql)
- [Faustin Lammler](https://github.com/fauust/ansible-role-mariadb)
