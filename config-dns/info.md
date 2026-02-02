## A zone transfer happens when a secondary DNS server wants to copy a zone from the primary DNS server.
- Primary = authoritative, editable (type master)
- Secondary = read-only copy (type slave)
- Communication uses TCP port 53, unlike normal queries (UDP 53)

## Primary checks:
- Is this server allowed to transfer the zone?
- Does the request match the IP / ACL?
- If allowed, primary sends all zone records to secondary
- Secondary saves them in read-only mode, so secondary can answer queries authoritatively.


## If Primary DNS is unreachable
SOA says:
dns.lab.local. admin.lab.local.

Secondary tries to contact dns.lab.local
- If dns.lab.local is:
    - Down
    - Wrong hostname
    - IP unreachable
- then Zone transfer fails
- Secondary has no updated records

## If Serial number mismatch / misconfiguration
- Serial number in SOA is not incremented on primary
- Secondary thinks no updates exist → may not pull new data
- Transfer can “fail silently” in terms of updates

## 
