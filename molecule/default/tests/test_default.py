#!/usr/bin/env python

import os
import stat
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


def test_shell(host):
    mariadb_server_debian = host.package("mariadb-server")
    mariadb_server_redhat = host.package("MariaDB-server")
    assert mariadb_server_debian.is_installed or mariadb_server_redhat.is_installed
