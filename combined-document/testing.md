## got nothing on dashboard (this one log)

## insert:
```
curl -k -u admin:SecretPassword -H "Content-Type: application/json" -X PUT "https://127.0.0.1:9200/wazuh-alerts-4.x-2026.02.05/_doc/anita-54321?refresh=true" -d "{\"@timestamp\":\"2026-02-05T11:00:00Z\",\"document_type\":\"combined\",\"user\":\"anita\",\"session\":54321,\"status\":\"active\",\"login_time\":\"2026-02-05T11:00:00Z\"}"
```

## search:
```
url -k -u admin:SecretPassword -H "Content-Type: application/json" -X GET "https://127.0.0.1:9200/wazuh-alerts-4.x-*/_search?pretty" -d "{\"query\":{\"term\":{\"_id\":\"user-54321\"}}}"
```
```
{
  "took" : 586,
  "timed_out" : false,
  "_shards" : {
    "total" : 48,
    "successful" : 48,
    "skipped" : 0,
    "failed" : 0
  },
  "hits" : {
    "total" : {
      "value" : 1,
      "relation" : "eq"
    },
    "max_score" : 1.0,
    "hits" : [
      {
        "_index" : "wazuh-alerts-4.x-2026.02.05",
        "_id" : "anita-54321",
        "_score" : 1.0,
        "_source" : {
          "@timestamp" : "2026-02-05T11:00:00Z",
          "document_type" : "combined",
          "user" : "user",
          "session" : 54321,
          "status" : "active",
          "login_time" : "2026-02-05T11:00:00Z"
        }
      }
    ]
  }
}
```


You can do existing log update by:
```
curl -k -u admin:SecretPassword -H "Content-Type: application/json" -X POST "https://127.0.0.1:9200/wazuh-alerts-4.x-2026.02.05/_update/NMzkLpwBNDuTFyZyJYeq?refresh=true" -d "{\"doc\":{\"data\":{\"extra_data\":\"anything-you-want\",\"status\":\"offline\"}}}"
```
