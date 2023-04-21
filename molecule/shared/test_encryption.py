#!/usr/bin/env python

def test_encryption_keys(host):
    encrypted_file = host.file("/etc/mysql/encryption/keys.enc")
    encrypted_key_file = host.file("/etc/mysql/encryption/password_file")
    assert encrypted_file.exists and encrypted_key_file.exists

def test_encryption_is_used(host):
    mysql_config = host.file("/etc/mysql/my.cnf")
    assert mysql_config.exists
    assert "file_key_management_filename" in mysql_config.content_string
