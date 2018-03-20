import requests
import config
import csv


class MatchEntryList:
    def __init__(self):
        self.list = []
        
    def add_entry(self, t1, t2, t3, vault, foul, total):
        t1 = t1[3:]
        t2 = t2[3:]
        t3 = t3[3:]
        self.list.append([t1, t2, t3, vault, foul, total])

    def get_teams_entries(self, team):
        team_entries = []
        for entry in self.list:
            if team in entry[:3]:
                team_entries.append(entry)
        return team_entries
        
    def export_as_csv(self, path):
        with open(path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["team1", "team2", "team3",
                             "vault", "foul", "total"])
            for entry in self.list:
                writer.writerow(entry)

def get_event_data(event):
    tba_base_url = "http://www.thebluealliance.com/api/v3/"

    payload = {"X-TBA-Auth-Key": config.tba_api_key}
    request_url = tba_base_url + "event/" + event + "/matches"
    request = requests.get(request_url, params=payload)


    match_entries = MatchEntryList()
    for match in request.json():
        rt1 = match["alliances"]["red"]["team_keys"][0]
        rt2 = match["alliances"]["red"]["team_keys"][1]
        rt3 = match["alliances"]["red"]["team_keys"][2]
        rv = match["score_breakdown"]["red"]["vaultPoints"]
        rf = match["score_breakdown"]["blue"]["foulPoints"]
        rt = match["score_breakdown"]["red"]["totalPoints"]
        match_entries.add_entry(rt1, rt2, rt3, rv, rf, rt)

        bt1 = match["alliances"]["blue"]["team_keys"][0]
        bt2 = match["alliances"]["blue"]["team_keys"][1]
        bt3 = match["alliances"]["blue"]["team_keys"][2]
        bv = match["score_breakdown"]["blue"]["vaultPoints"]
        bf = match["score_breakdown"]["red"]["foulPoints"]
        bt = match["score_breakdown"]["blue"]["totalPoints"]
        match_entries.add_entry(bt1, bt2, bt3, bv, bf, bt)

    match_entries.export_as_csv("data/" + event + ".csv")

if __name__ == "__main__":
    events = ["2018ctwat", "2018ctsct"]
    for event in events:
        get_event_data(event)
