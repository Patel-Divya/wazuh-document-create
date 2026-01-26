# ossec.conf
```
<ossec_config>
  <remote>
    <connection>syslog</connection>
    <protocol>udp</protocol>
    <port>514</port>
  </remote>
</ossec_config>
```

# Decoder
```
<decoder name="zabbix-trigger">
  <prematch>Zabbix trigger: </prematch>
  <plugin_decoder offset="after_prematch">JSON_Decoder</plugin_decoder>
</decoder>
```

# Rule
```
<!-- Local rules -->
<!-- Modify it at your will. -->
<!-- Copyright (C) 2015, Wazuh Inc. -->

<group name="local,wazuh,agent_state,">

  <!-- =====================================================
       Wrapper for predefined rule 503 (Agent started)
       Enables Active Response execution
       ===================================================== -->
  <rule id="100503" level="10">
    <if_sid>503</if_sid>
    <description>Agent started (Active Response enabled)</description>
    <options>no_full_log</options>
    <group>wazuh_agent_started,</group>
  </rule>

  <!-- =====================================================
       Wrapper for predefined rule 506 (Agent stopped)
       Enables Active Response execution
       ===================================================== -->
  <rule id="100506" level="10">
    <if_sid>506</if_sid>
    <description>Agent stopped (Active Response enabled)</description>
    <options>no_full_log</options>
    <group>wazuh_agent_stopped,</group>
  </rule>

</group>

<!-- Main rule -->
<group name="zabbix,trigger">

  <rule id="120501" level="3">
    <field name="severity">Information</field>
    <description>Zabbix Trigger (Info)</description>
  </rule>

  <rule id="120502" level="7">
    <field name="severity">Warning</field>
    <description>Zabbix Trigger (Warning)</description>
  </rule>

  <rule id="120503" level="10">
    <field name="severity">High</field>
    <description>Zabbix Trigger (High)</description>
  </rule>

  <rule id="120504" level="13">
    <field name="severity">Critical</field>
    <description>Zabbix Trigger (Critical)</description>
  </rule>

</group>
```

# validate rule & decoder
goto: 
``` 
/var/ossec/bin/wazuh-logtest
```
paste: 
``` 
Zabbix trigger: {"severity":"Critical","host":"windows-poc","trigger":"CPU High","status":"PROBLEM"}
```


# Test from Windows
PowerShell UDP test:
```
$udpClient = New-Object System.Net.Sockets.UdpClient
$udpClient.Connect("127.0.0.1",514)

$msg = 'Zabbix trigger: {"severity":"Critical","host":"windows-poc","trigger":"CPU High","status":"PROBLEM"}'
$bytes = [System.Text.Encoding]::UTF8.GetBytes($msg)

$udpClient.Send($bytes,$bytes.Length)
$udpClient.Close()
```

# Validation:
```
docker exec -it wazuh-manager cat /var/ossec/logs/alerts/alerts.json | tail -20
```

