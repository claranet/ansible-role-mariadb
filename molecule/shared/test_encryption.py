#!/usr/bin/env python

def get_mysql_config_path(host):
    config_path = ""
    os_release = host.file('/etc/os-release')
    for os in ('centos', 'fedora', 'rhel','amzn', 'rocky', 'almalinux'):
        if os_release.contains(f'ID="{os}"'):
            config_path = "/etc/my.cnf.d/99-ansible-role-mariadb-my.cnf"
            break
        else:
            config_path = "/etc/mysql/mariadb.conf.d/99-ansible-role-mariadb-my.cnf"

    return config_path

def test_encryption_keys(host):
    encrypted_file = host.file("/etc/mysql/encryption/keys.enc")
    encrypted_key_file = host.file("/etc/mysql/encryption/password_file")
    assert encrypted_file.exists and encrypted_key_file.exists


def test_encryption_is_used(host):
    mysql_config = host.file(get_mysql_config_path(host))
    assert mysql_config.exists
    assert "file_key_management_filename" in mysql_config.content_string
