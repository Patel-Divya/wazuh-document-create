Goto:
C:\Program Files (x86)\ossec-agent\logs\ossec.log

Add EventID filtering for noisy logs:
<ossec_config>
  ...
  <localfile>
    <location>Security</location>
    <log_format>eventchannel</log_format>

    <!-- Exclude noisy Kerberos failed events -->
    <exclude_event_id>4768</exclude_event_id>
    <exclude_event_id>4769</exclude_event_id>
    <exclude_event_id>4771</exclude_event_id>
  </localfile>
  ...
</ossec_config>

Note:
You will se somthing like:
<localfile> <location>Security</location> <log_format>eventchannel</log_format> <query>Event/System[EventID != 5145 and EventID != 5156 and EventID != 5447 and EventID != 4656 and EventID != 4658 and EventID != 4663 and EventID != 4660 and EventID != 4670 and EventID != 4690 and EventID != 4703 and EventID != 4907 and EventID != 5152 and EventID != 5157]</query> </localfile>

Add event IDs to exclude: EventID != 4768 and EventID != 4769 and EventID != 4771


Restart agent:
net stop wazuh
net start wazuh

Filter verify:
C:\Program Files (x86)\ossec-agent\logs\ossec.log
 (doesm't work for me)
