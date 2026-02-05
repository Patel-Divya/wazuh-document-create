## Step 1: Create a new index template
```
PUT _index_template/custom-sessions-template
{
  "index_patterns": ["custom-sessions-*"],
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0
    },
    "mappings": {
      "properties": {
        "@timestamp": { "type": "date" },
        "user": { "type": "keyword" },
        "session": { "type": "long" },
        "status": { "type": "keyword" },
        "extra_data": { "type": "text" }
      }
    }
  }
}
```
## Step 2: Create the initial index + alias
```
PUT custom-sessions-000001
{
  "aliases": {
    "custom-sessions-alias": { "is_write_index": true }
  },
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "properties": {
      "@timestamp": { "type": "date" },
      "user": { "type": "keyword" },
      "session": { "type": "long" },
      "status": { "type": "keyword" },
      "extra_data": { "type": "text" }
    }
  }
}
```


## Step 3: Create ISM policy for auto-delete
```
PUT _plugins/_ism/policies/custom-sessions-ism
{
  "policy": {
    "description": "Delete testing custom sessions after 15 minutes",
    "default_state": "hot",
    "states": [
      {
        "name": "hot",
        "actions": [],
        "transitions": [
          {
            "state_name": "delete",
            "conditions": {
              "min_index_age": "15m"
            }
          }
        ]
      },
      {
        "name": "delete",
        "actions": [
          {
            "delete": {}
          }
        ],
        "transitions": []
      }
    ]
  }
}
```

## Step 4: Attach ISM policy to the index
```
PUT custom-sessions-000001/_settings
{
  "index": {
    "opendistro.index_state_management.policy_id": "custom-sessions-ism"
  }
}
```

## Step 5: Insert a test document
```
POST custom-sessions-alias/_doc?refresh=true
{
  "@timestamp": "2026-02-05T11:00:00Z",
  "user": "anita",
  "session": 54321,
  "status": "active",
  "extra_data": "testing"
}
```

## note: auto delete not worked.

## to add the index pattern, 
Goto: Dashbpard management > index patterns > create
