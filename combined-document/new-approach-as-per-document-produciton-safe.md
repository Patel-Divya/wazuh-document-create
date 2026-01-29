# **Step-by-Step: VPN Events Index with Template, Rollover, and Auto-Delete**

---

## **Step 1️: Decide your index pattern**

* Use a pattern like:
```
vpn-events-*
```

* This allows **rotated indices** (e.g., `vpn-events-000001`, `vpn-events-000002`)
* All logs will go into indices that match this pattern.

---

## **Step 2️: Create the Index Template**

* OpenSearch template defines **mappings, rollover settings, and optional lifecycle policy**.

* Example using `curl`:

```bash
curl -k -u admin:SecretPassword -X PUT "https://localhost:9200/_index_template/vpn-events-template" \
-H "Content-Type: application/json" \
-d '{
  "index_patterns": ["vpn-events-*"],
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 1,
      "index.lifecycle.name": "vpn-events-ilm",
      "index.lifecycle.rollover_alias": "vpn-events"
    },
    "mappings": {
      "properties": {
        "@timestamp": { "type": "date" },
        "user": { "type": "keyword" },
        "session_id": { "type": "keyword" },
        "login_time": { "type": "date" },
        "logout_time": { "type": "date" },
        "status": { "type": "keyword" },
        "source": { "type": "keyword" },
        "action": { "type": "keyword" },
        "event_type": { "type": "keyword" }
      }
    }
  },
  "priority": 500
}'
```

**Notes:**

* `index.lifecycle.name` → ILM policy we will create in Step 3
* `index.lifecycle.rollover_alias` → alias you’ll use in Python script (`vpn-events/_doc`)
* `vpn-events-*` → pattern for rotated indices

---

## **Step 3️: Create a Lifecycle Policy (ILM)**

* This controls **rollover** and **auto-deletion**.
* Example: rollover every 50 MB or 1 day, delete after 30 days:

```bash
curl -k -u admin:SecretPassword -X PUT "https://localhost:9200/_ilm/policy/vpn-events-ilm" \
-H "Content-Type: application/json" \
-d '{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_size": "50mb",
            "max_age": "1d"
          }
        }
      },
      "delete": {
        "min_age": "30d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}'
```

---

## **Step 4️: Create the initial index with alias**

* The **alias** is what your Python script will use (`vpn-events`).
* OpenSearch will create the first physical index (`vpn-events-000001`) and link the alias:

```bash
curl -k -u admin:SecretPassword -X PUT "https://localhost:9200/vpn-events-000001" \
-H "Content-Type: application/json" \
-d '{
  "aliases": {
    "vpn-events": {
      "is_write_index": true
    }
  }
}'
```

* After this, your script can continue using:

```
POST https://localhost:9200/vpn-events/_doc
```

* OpenSearch will write to `vpn-events-000001`. When rollover happens, it writes to the next index automatically.

---

## **Step 5️: Adjust your Python script (minimal changes)**

* **Insert documents:** ✅ same as before:

```python
event = {
    "@timestamp": now(),
    "event_type": "vpn_connect",
    "user": user,
    "session_id": session_id,
    "source": "vpn-poc",
    "action": "connect"
}

resp = os_session.post(
    f"{OPENSEARCH_URL}/vpn-events/_doc",
    json=event,
    timeout=10
)
```

* **Update documents:** ✅ same as before:

```python
update_event = {
    "doc": {
        "logout_time": now(),
        "status": "disconnected"
    }
}

resp = os_session.post(
    f"{OPENSEARCH_URL}/vpn-events/_update/<doc_id>",
    json=update_event,
    timeout=10
)
```

> OpenSearch handles rollover, alias, and mapping automatically — your script doesn’t need to know `vpn-events-000001` vs `vpn-events-000002`.

---

## **Step 6️: Optional — Visualize in OpenSearch Dashboards**

1. Go to **Stack Management → Index Patterns**
2. Create a pattern: `vpn-events*`
3. Set `@timestamp` as the time field
4. Build dashboards and visualize active sessions

---

## **Result**

* Logs inserted by your script automatically go to `vpn-events-000001` (or rotated index)
* Automatic rollover occurs when index is full or 1 day passes
* Old indices are auto-deleted after 30 days
* Your Python script **doesn’t change at all**
* Full integration with OpenSearch features like ILM and dashboards

---

If you want, I can also **write the exact full Python + OpenSearch setup** for **login/logout combined sessions**, so your final index looks like:

```json
{
  "user": "alice",
  "session_id": "abc123",
  "login_time": "...",
  "logout_time": "...",
  "status": "active",
  "@timestamp": "...",
  "source": "vpn-poc"
}
```

…ready for live dashboards.

Do you want me to do that next?
