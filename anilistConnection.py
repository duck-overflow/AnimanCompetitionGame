import requests
import time

from database import insert_activity, get_all_activity_ids
from datetime import datetime

def transfer_username_id(username):
    query = '''
    query ($name: String) {
    User(name: $name) {
        id
        name
        }
    }
    '''
    variables = {"name": username}
    res = requests.post("https://graphql.anilist.co", json={"query": query, "variables": variables})
    res.raise_for_status()
    if not res.ok:
        print("[!] Fehler beim übersetzen des Nutzernamens zur ID:", res.text)
        res.raise_for_status()
    return res.json()["data"]["User"]["id"]

def fetch_anilist_activities(username):
    query = '''
    query ($id: Int) {
    Page(perPage: 5) {
    activities(userId: $id, type: MEDIA_LIST, sort: ID_DESC) {
      ... on ListActivity {
        id
        createdAt
        status
        progress
        media {
          id
          title {
            romaji
          }
          type
        }
      }
    }
  }
}
    '''
    variables = {"id": transfer_username_id(username)}
    res = requests.post("https://graphql.anilist.co", json={"query": query, "variables": variables})
    res.raise_for_status()
    if not res.ok:
        print("Fehlerantwort:", res.text)
        res.raise_for_status()
    return res.json()["data"]["Page"]["activities"]

def process_activities(username):
    activities = fetch_anilist_activities(transfer_username_id(username))
    started = datetime.now()
    print(f"[>] Neuer Suchdurchlauf gestartet! {started}")

    for act in activities:
        aid = str(act["id"])
        seen_ids = get_all_activity_ids(username)

        if aid in seen_ids:
            continue

        dt = datetime.fromtimestamp(act["createdAt"])
        createdAt = dt.strftime("%Y-%m-%d %H:%M:%S")
        title = act["media"]["title"]["romaji"]
        mediaType = act["media"]["type"]

        if not ("watched" in act["status"] or "read" in act["status"]):
            insert_activity(
                createdAt,
                aid,
                title,
                act["status"].upper(),
                mediaType
            )
            print(f"[+] Neue Aktivität (kein Fortschritt): {title} | {act['status']} | {mediaType}")
            continue

        if act["progress"] is None:
            insert_activity(
                createdAt,
                aid,
                title,
                act["status"].upper(),
                mediaType
            )
            print(f"[+] Neue Aktivität (kein Fortschritt): {title} | {act['status']} | {mediaType}")
            continue

        progress = act["progress"].split()
        if len(progress) == 1:
            ch_start = progress[0]
            ch_end = ch_start
        else:
            ch_start = progress[0]
            ch_end = progress[2]

        print(f"[+] Neue Aktivität: {title} {ch_start}-{ch_end} | {mediaType}")

        insert_activity(
            createdAt,
            aid,
            title,
            f"{ch_start} - {ch_end}",
            mediaType
        )

    print(f"[>] Neuer Suchdurchlauf beendet!  Abgeschlossen in {datetime.now() - started}")


def fetch_all_anilist_activities(username):
    page = 1
    per_page = 50
    all_activities = []

    while True:
        query = '''
        query ($id: Int, $page: Int, $perPage: Int) {
          Page(page: $page, perPage: $perPage) {
            pageInfo {
              hasNextPage
            }
            activities(userId: $id, type: MEDIA_LIST, sort: ID_DESC) {
              ... on ListActivity {
                id
                createdAt
                status
                progress
                media {
                  id
                  title {
                    romaji
                  }
                  type
                }
              }
            }
          }
        }
        '''
        variables = {
            "id": transfer_username_id(username),
            "page": page,
            "perPage": per_page
        }

        res = requests.post("https://graphql.anilist.co", json={"query": query, "variables": variables})
        res.raise_for_status()
        data = res.json()

        activities = data["data"]["Page"]["activities"]
        all_activities.extend(activities)

        if not data["data"]["Page"]["pageInfo"]["hasNextPage"]:
            break
        page += 1
        time.sleep(0.2)  # vermeidet Rate Limits

    return all_activities

def bulk_import_activities(username):
    activities = fetch_all_anilist_activities(transfer_username_id(username))
    started = datetime.now()
    print(f"[>] Starte BULK-Import ({len(activities)} Aktivitäten)...")

    for act in activities:
        aid = str(act["id"])
        seen_ids = get_all_activity_ids(username)

        if aid in seen_ids:
            continue

        dt = datetime.fromtimestamp(act["createdAt"])
        createdAt = dt.strftime("%Y-%m-%d %H:%M:%S")
        title = act["media"]["title"]["romaji"]
        mediaType = act["media"]["type"]

        if not ("watched" in act["status"] or "read" in act["status"]):
            insert_activity(
                createdAt,
                aid,
                title,
                act["status"].upper(),
                mediaType
            )
            print(f"[+] [BULK] Neue Aktivität (kein Fortschritt): {title} | {act['status']} | {mediaType}")
            continue

        if act["progress"] is None:
            insert_activity(
                createdAt,
                aid,
                title,
                act["status"].upper(),
                mediaType
            )
            print(f"[+] [BULK] Neue Aktivität (kein Fortschritt): {title} | {act['status']} | {mediaType}")
            continue

        progress = act["progress"].split()
        if len(progress) == 1:
            ch_start = progress[0]
            ch_end = ch_start
        else:
            ch_start = progress[0]
            ch_end = progress[2]

        insert_activity(
            createdAt,
            aid,
            title,
            f"{ch_start} - {ch_end}",
            mediaType
        )
        print(f"[+] [BULK] Neue Aktivität: {title} {ch_start}-{ch_end} | {mediaType}")

    print(f"[>] BULK-Import abgeschlossen in {datetime.now() - started}")
