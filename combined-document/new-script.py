#!/usr/bin/env python3

import sys
import json
import requests

DEBUG_FILE = "/var/ossec/tmp/active_users_debug.log"

OPENSEARCH_URL = "https://127.0.0.1:9200"
OPENSEARCH_USER = "admin"
OPENSEARCH_PASS = "password"

HEADERS = {"Content-Type": "application/json"}


def log_debug(msg):
    with open(DEBUG_FILE, "a") as f:
        f.write(msg + "\n")


def os_post(url, payload):
    return requests.post(
        url,
        auth=(OPENSEARCH_USER, OPENSEARCH_PASS),
        headers=HEADERS,
        json=payload,
        verify=False,
        timeout=10
    )


def os_put(url, payload):
    return requests.put(
        url,
        auth=(OPENSEARCH_USER, OPENSEARCH_PASS),
        headers=HEADERS,
        json=payload,
        verify=False,
        timeout=10
    )


def main():
    alert_file = sys.argv[1]

    with open(alert_file, "r") as f:
        alert = json.load(f)

    alert_ts = alert.get("@timestamp")
    data = alert.get("data", {})

    # Extract fields
    logdesc = data.get("logdesc")
    tunnelip = data.get("tunnelip")
    tunnelid = data.get("tunnelid")
    dstuser = data.get("dstuser")
    remip = data.get("remip")
    subtype = data.get("subtype")

    sentbyte = data.get("sentbyte")
    rcvdbyte = data.get("rcvdbyte")

    # Only continue if tunnelip exists
    if not tunnelip:
        log_debug("Tunnel IP missing, skipping session logic")
        return

    doc_id = f"{dstuser}-{tunnelid}"

    # ------------------------------------------------------------------
    # CASE 1: SSL VPN TUNNEL UP  → SEARCH + INSERT
    # ------------------------------------------------------------------
    if logdesc == "SSL VPN tunnel up":

        search_query = {
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"data.subtype": subtype}},
                        {"term": {"data.tunnelid": tunnelid}},
                        {"term": {"data.dstuser": dstuser}},
                        {"term": {"data.logdesc": logdesc}},
                        {"term": {"data.remip": remip}},
                        {"term": {"data.tunnelip": tunnelip}}
                    ]
                }
            },
            "size": 1
        }

        log_debug("Searching existing tunnel-up event")

        resp = os_post(
            f"{OPENSEARCH_URL}/wazuh-alerts-4.x-*/_search",
            search_query
        )

        if resp.status_code != 200:
            log_debug(f"Search failed: {resp.text}")
            return

        hits = resp.json().get("hits", {}).get("hits", [])

        if not hits:
            log_debug("No matching tunnel-up document found")
            return

        hit = hits[0]
        index = hit["_index"]
        source = hit["_source"]

        session_start = source.get("timestamp") or source.get("@timestamp")

        combined_doc = {
            "@timestamp": source.get("@timestamp"),
            "timestamp": source.get("timestamp"),
            "session_start": session_start,
            "status": "active",
            "log_type": "combined"
        }

        log_debug(f"Inserting combined session doc into {index}")

        put_resp = os_put(
            f"{OPENSEARCH_URL}/{index}/_doc/{doc_id}?refresh=true",
            combined_doc
        )

        log_debug(f"Insert response: {put_resp.status_code} {put_resp.text}")

    # ------------------------------------------------------------------
    # CASE 2: SSL VPN TUNNEL DOWN → UPDATE
    # ------------------------------------------------------------------
    elif logdesc == "SSL VPN tunnel down":

        update_doc = {
            "doc": {
                "@timestamp": alert_ts,
                "session_end": alert_ts,
                "status": "closed",
                "data.sentbyte": sentbyte,
                "data.rcvdbyte": rcvdbyte
            }
        }

        log_debug(f"Updating session doc {doc_id}")

        update_resp = requests.post(
            f"{OPENSEARCH_URL}/wazuh-alerts-4.x-*/_update/{doc_id}",
            auth=(OPENSEARCH_USER, OPENSEARCH_PASS),
            headers=HEADERS,
            json=update_doc,
            verify=False,
            timeout=10
        )

        log_debug(f"Update response: {update_resp.status_code} {update_resp.text}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        log_debug("ERROR: alert file argument missing")
        sys.exit(1)

    main()
