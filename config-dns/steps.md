Notes:
## Forward Lookup Zone:
Resolves hostname → IP
Contains:
```
A
AAAA
CNAME
MX
```

## Reverse Lookup Zone:
- Resolves IP → hostname
- Uses PTR records
- Required for logging, security, and some services


## Questitons:
- All records A, AAAA, CNAME, MX, NS, PTR, TXT
- What are DNS zones, what are forwarders, what are reverse lookups
- Which record in which zone (forward or reverse), and why


create 2 VM.
- Create new network for host only adaptor, and enable DHCP in it.
- Make both on host only adaptor, and select newly created network.
- Make sure both gets different IP.



## ON server:
``` bash
sudo apt update
sudo apt install bind9 bind9utils bind9-dnsutils -y
systemctl status bind9
```

Edit zone config:
```bash
sudo nano /etc/bind/named.conf.local

sudo nano /etc/bind/named.conf.local
```
```bash
zone "lab.local" {
    type master;
    file "/etc/bind/db.lab.local";
};

zone "145.168.192.in-addr.arpa" {
    type master;
    file "/etc/bind/db.192.168.145";
};
```


Create Forward Lookup Zone:
``` bash
sudo cp /etc/bind/db.local /etc/bind/db.lab.local
sudo nano /etc/bind/db.lab.local
```

Replace the file with:
```bash
$TTL    604800
@   IN  SOA dns.lab.local. admin.lab.local. (
            2
            604800
            86400
            2419200
            604800 )

@       IN  NS  dns.lab.local.
dns     IN  A   192.168.145.3
server1 IN  A   192.168.145.4
www     IN  CNAME server1
```


Create Reverse Lookup Zone:
```bash
sudo cp /etc/bind/db.127 /etc/bind/db.192.168.145
sudo nano /etc/bind/db.192.168.145
```

Edit to:
```bash
$TTL    604800
@   IN  SOA lab.local. admin.lab.local. (
            1
            604800
            86400
            2419200
            604800 )

@       IN  NS  dns.lab.local.
3       IN  PTR dns.lab.local.
4       IN  PTR server1.lab.local.
```

Check Configuration (DO NOT SKIP):
```bash
sudo named-checkconf
sudo named-checkzone lab.local /etc/bind/db.lab.local
sudo named-checkzone 145.168.192.in-addr.arpa /etc/bind/db.192.168.145
```

Restart DNS Service:
```bash
sudo systemctl restart bind9
sudo systemctl status bind9
```


## Configure Client to Use DNS:
On 192.168.145.4:

Edit resolver:
```bash
sudo nano /etc/systemd/resolved.conf
```

Set:
```bash
DNS=192.168.145.3
Domains=lab.local
```

Apply:
```bash
sudo systemctl restart systemd-resolved
```

Verify:
```bash
resolvectl status
```

## TEST EVERYTHING (This Is What Matters)
From Client Server:
```bash
nslookup server1.lab.local
nslookup www.lab.local
nslookup 192.168.145.3
nslookup 192.168.145.4
ping server1.lab.local
```
