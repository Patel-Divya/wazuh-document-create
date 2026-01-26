# Big picture (one glance)

**how Zabbix sends alerts**.

```
Zabbix Trigger fires
   ↓
Zabbix Media Type (script)
   ↓
Script writes JSON log file
   ↓
Wazuh Agent reads that file
   ↓
Wazuh Manager → Threat Hunting
```
---


## STEP 1 — Install Wazuh Agent on the Zabbix server
```bash
curl -sO https://packages.wazuh.com/4.x/wazuh-install.sh
sudo bash wazuh-install.sh --agent
```

Configure agent (`/var/ossec/etc/ossec.conf`):

```xml
<client>
  <server-ip>192.168.29.77</server-ip>
</client>

<localfile>
  <log_format>json</log_format>
  <location>/var/log/zabbix/zabbix_triggers.json</location>
</localfile>
```

Restart agent:
```bash
sudo systemctl restart wazuh-agent
```

---
## STEP 2 — Create the log file
Zabbix will write alerts here.

```bash
sudo mkdir -p /var/log/zabbix
sudo chown zabbix:zabbix /var/log/zabbix
```

File:
```
/var/log/zabbix/zabbix_triggers.json
```

---

## STEP 3 — Create the Zabbix alert script
Zabbix uses **Media Types** to send alerts.
A **script media type** is the cleanest.

Create script:
```bash
sudo nano /usr/lib/zabbix/alertscripts/zabbix_to_wazuh.sh
```

Paste (change it accordingy):
```bash
#!/bin/bash

SEVERITY="$1"
HOST="$2"
TRIGGER="$3"
STATUS="$4"
EVENTID="$5"

LOGFILE="/var/log/zabbix/zabbix_triggers.json"
TIMESTAMP=$(date -Is)

echo "{\"source\":\"zabbix\",\"severity\":\"$SEVERITY\",\"host\":\"$HOST\",\"trigger\":\"$TRIGGER\",\"status\":\"$STATUS\",\"eventid\":\"$EVENTID\",\"timestamp\":\"$TIMESTAMP\"}" >> "$LOGFILE"
```

Permissions:
```bash
sudo chmod +x /usr/lib/zabbix/alertscripts/zabbix_to_wazuh.sh
sudo chown zabbix:zabbix /usr/lib/zabbix/alertscripts/zabbix_to_wazuh.sh
```

---
## STEP 4 — Test WITHOUT Zabbix UI
Run as Zabbix user:
```bash
sudo -u zabbix /usr/lib/zabbix/alertscripts/zabbix_to_wazuh.sh \
  Critical windows-poc "CPU High" PROBLEM 12345
```

Check file:
```bash
cat /var/log/zabbix/zabbix_triggers.json
```

You should see **one JSON line**.

---
## STEP 5 — Configure Zabbix Media Type
Zabbix UI → **Administration → Media types → Create**

* Type: **Script**
* Script name: `zabbix_to_wazuh.sh`
* Parameters (ORDER MATTERS):

```
{TRIGGER.SEVERITY}
{HOST.NAME}
{TRIGGER.NAME}
{TRIGGER.STATUS}
{EVENT.ID}
```

---

## STEP 6 — Create Zabbix Action
Zabbix → **Configuration → Actions**

* Event source: **Triggers**
* Condition: Severity ≥ Warning
* Operation: Send message → Media type (created above)


---

# What happens now (end-to-end)

1. Trigger fires in Zabbix
2. Zabbix runs the script
3. Script appends **one JSON line**
4. Wazuh Agent reads **only the new line**
5. Wazuh Manager applies your decoder + rules
6. Alert appears in **Threat Hunting**
