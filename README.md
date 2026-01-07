Goto:
```
C:\Program Files (x86)\ossec-agent\ossec.conf
```

Add EventID filtering for noisy logs:
```bash
<ossec_config>
  ...
  <localfile>
    <location>Security</location>
    <log_format>eventchannel</log_format>
    <query>.....</query>
  </localfile>
  ...
</ossec_config>
```

Note:
You will se somthing like:
```bash
<localfile> 
  <location>Security</location> 
  <log_format>eventchannel</log_format> 
  <query>
    Event/System[EventID != 5145 and EventID != 5156 and EventID != 5447 and EventID != 4656 and EventID != 4658 and EventID != 4663 and EventID != 4660 and EventID != 4670 and EventID != 4690 and EventID != 4703 and EventID != 4907 and EventID != 5152 and EventID != 5157]
  </query> 
</localfile>
```

Add to exclude event IDs:
```bash
EventID != 4769
```

Restart agent:
```bash
net stop wazuh
net start wazuh
```

Verify filter logs on:
```bash
C:\Program Files (x86)\ossec-agent\logs\ossec.log
```

(does not show all time for me, but it works)
