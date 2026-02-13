class users {
  user { 'adminuser':
    ensure     => present,
    managehome => true,
    shell      => '/bin/bash',
  }

  file { '/home/adminuser/.ssh':
    ensure => directory,
    owner  => 'adminuser',
    group  => 'adminuser',
    mode   => '0700',
  }
}
