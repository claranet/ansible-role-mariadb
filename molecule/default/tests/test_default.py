#!/usr/bin/env python


def test_package_is_installed(host):
    mariadb_server_debian = host.package("mariadb-server")
    mariadb_server_redhat = host.package("MariaDB-server")
    assert mariadb_server_debian.is_installed or mariadb_server_redhat.is_installed


def test_service_listening(host):
    assert host.socket("tcp://0.0.0.0:3306").is_listening
