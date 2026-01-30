Step 1️⃣ Configure BIND to forward to host

Edit:
```
sudo nano /etc/bind/named.conf.options
```

Use:
```
options {
    directory "/var/cache/bind";

    recursion yes;

    forwarders {
        192.168.56.1;
    };

    forward only;

    listen-on { any; };
    allow-query { any; };
};
```

Apply:
```
sudo named-checkconf
sudo systemctl restart bind9
```
Step 2️⃣ Test DNS connectivity to host (this matters)

From DNS VM:
```
dig @192.168.56.1 google.com
```
