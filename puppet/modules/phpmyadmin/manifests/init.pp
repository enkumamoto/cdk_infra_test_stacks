class phpmyadmin {
  package { ['httpd', 'php', 'php-mysqli']:
    ensure => installed,
  }

  package { 'phpmyadmin':
    ensure => installed,
  }

  service { 'httpd':
    ensure => running,
    enable => true,
  }
}
