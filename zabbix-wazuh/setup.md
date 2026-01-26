# ossec conf:
<ossec_config>
  <remote>
    <connection>syslog</connection>
    <protocol>udp</protocol>
    <port>514</port>
  </remote>
</ossec_config>


# Decoder:
<decoders>
  <decoder name="zabbix-trigger">
    <prematch>Zabbix trigger: </prematch>
    <plugin_decoder offset="after_prematch">JSON_Decoder</plugin_decoder>
  </decoder>
</decoders>


# Rule:
<group name="zabbix,trigger">
  <rule id="100500" level="3">
    <if_matched_sid>zabbix-trigger</if_matched_sid>
    <description>Zabbix Trigger Alert</description>
    <!-- Dynamic severity → level mapping -->
    <field name="severity">Information</field>
    <level>3</level>
    <field name="severity">Warning</field>
    <level>7</level>
    <field name="severity">High</field>
    <level>10</level>
    <field name="severity">Critical</field>
    <level>13</level>
  </rule>
</group>


# validate rule & decoder:
goto: /var/ossec/bin/wazuh-logtest
paste: Zabbix trigger: {"severity":"Critical","host":"windows-poc","trigger":"CPU High","status":"PROBLEM"}


# Test from Windows:
# PowerShell UDP test:
$udpClient = New-Object System.Net.Sockets.UdpClient
$udpClient.Connect("127.0.0.1",514)

$msg = 'Zabbix trigger: {"severity":"Critical","host":"windows-poc","trigger":"CPU High","status":"PROBLEM"}'
$bytes = [System.Text.Encoding]::UTF8.GetBytes($msg)

$udpClient.Send($bytes,$bytes.Length)
$udpClient.Close()


# Validation:
docker exec -it wazuh-manager cat /var/ossec/logs/alerts/alerts.json | tail -20

