import requests
import config
import csv
import numpy as np


class MatchEntryList:
    def __init__(self, event_key):
        self.list = []
        self.event = event_key
        
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
        
    def export_as_csv(self, path=None):
        if not path:
            path = "data/" + event + ".csv"

        with open(path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["team1", "team2", "team3",
                             "vault", "foul", "total"])
            for entry in self.list:
                writer.writerow(entry)

    def get_binary_matrix(self, score_type):
        # score_type should be one of: "vault", "foul", "total"
        all_teams = []
        for entry in self.list:
            all_teams.extend(entry[:3])
        all_teams = sorted(list(set(all_teams)))

        bin_matrix = np.zeros(shape=(len(self.list), len(all_teams)), dtype=int)
        for i in range(len(self.list)):
            entry = self.list[i]
            it1 = all_teams.index(entry[0])
            it2 = all_teams.index(entry[1])
            it3 = all_teams.index(entry[2])

            bin_matrix[i][it1] = 1
            bin_matrix[i][it2] = 1
            bin_matrix[i][it3] = 1

        if score_type == "vault":
            score_matrix = np.array(self.list, dtype=int)[:, 3].reshape(len(self.list), 1)
        elif score_type == "foul":
            score_matrix = np.array(self.list, dtype=int)[:, 4].reshape(len(self.list), 1)
        elif score_type == "total":
            score_matrix = np.array(self.list, dtype=int)[:, 5].reshape(len(self.list), 1)
        else:
            return

        return bin_matrix, score_matrix

    def export_binary_matrices(self, score_type, bin_path=None, s_path=None):
        if not bin_path:
            bin_path = "data/" + self.event + "_bin.csv"
        if not s_path:
            s_path = "data/" + self.event + "_scores.csv"

        bin_matrix, score_matrix = self.get_binary_matrix(score_type)

        with open(bin_path, 'w', newline='') as bin_file:
            bin_writer = csv.writer(bin_file)
            for row in bin_matrix:
                bin_writer.writerow(row)

        with open(s_path, 'w', newline='') as s_file:
            s_writer = csv.writer(s_file)
            for row in score_matrix:
                s_writer.writerow(row)

    def get_power_rankings(self, score_type):
        pass

def get_event_data(event):
    tba_base_url = "http://www.thebluealliance.com/api/v3/"

    payload = {"X-TBA-Auth-Key": config.tba_api_key}
    request_url = tba_base_url + "event/" + event + "/matches"
    request = requests.get(request_url, params=payload)


    match_entries = MatchEntryList(event)
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

    match_entries.export_as_csv()
    return match_entries

if __name__ == "__main__":
    events = ["2018ctwat", "2018ctsct"]
    data = []
    for event in events:
        entries = get_event_data(event)
        data.append(entries)

    data[0].export_binary_matrices("total")
