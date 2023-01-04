Basic steps inside a server:

```
$ sudo dnf update -y
$ sudo dnf install -y caddy fail2ban git

# Make sure all the services are running permanently
$ sudo systemctl enable caddy
$ sudo systemctl start caddy
$ sudo systemctl enable fail2ban
$ sudo systemctl start fail2ban

$ cd /usr/share/caddy
$ sudo rm -rf *
$ cd ~
$ git clone https://github.com/eatonphil/eatonphil.com

# Set up logs
$ sudo mkdir /var/log/caddy
$ sudo chown -R caddy:caddy /var/log/caddy
```

Tips:

* /usr/share/caddy directory should all be owned by caddy:caddy: `sudo chown -R caddy:caddy /usr/share/caddy`
* If you get permission denied errors, [you should `restorecon` to fix `SELiunx` settings](https://caddy.community/t/caddy-file-server-gives-403-error-forbidden-if-started-with-systemctl/11296/6): `sudo restorecon -r /usr/share/caddy/`
