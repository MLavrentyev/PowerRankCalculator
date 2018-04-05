import requests
import config
import csv
import numpy as np
import os
from datetime import date, datetime


tba_base_url = "http://www.thebluealliance.com/api/v3/"


class MatchEntryList:
    def __init__(self, event_keys):
        self.list = []
        self.event = event_keys
        
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

    def get_sorted_team_list(self):
        all_teams = []
        for entry in self.list:
            all_teams.extend(entry[:3])
        all_teams = sorted(list(set(all_teams)))
        return all_teams

    def export_as_csv(self, path=None):
        if not path:
            path = "data/" + self.event + "/" + self.event + ".csv"
        if not os.path.exists(path.rsplit("/", 1)[0]):
            os.makedirs(path.rsplit("/", 1)[0])

        with open(path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["team1", "team2", "team3",
                             "vault", "foul", "total"])
            for entry in self.list:
                writer.writerow(entry)

    def get_binary_matrices(self, score_type):
        # score_type should be one of: "vault", "foul", "total"
        all_teams = self.get_sorted_team_list()

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
            score_matrix = np.matrix(self.list, dtype=int)[:, 3].reshape(len(self.list), 1)
        elif score_type == "foul":
            score_matrix = np.matrix(self.list, dtype=int)[:, 4].reshape(len(self.list), 1)
        elif score_type == "total":
            score_matrix = np.matrix(self.list, dtype=int)[:, 5].reshape(len(self.list), 1)
        else:
            return

        return np.matrix(bin_matrix), score_matrix

    def export_binary_matrices(self, score_type, bin_path=None, s_path=None):
        if not bin_path:
            bin_path = "data/" + self.event + "/" + self.event + "_bin.csv"
        if not s_path:
            s_path = "data/" + self.event + "_scores.csv"
        if not os.path.exists(s_path.rsplit("/", 1)[0]):
            os.makedirs(s_path.rsplit("/", 1)[0])
        if not os.path.exists(bin_path.rsplit("/", 1)[0]):
            os.makedirs(bin_path.rsplit("/", 1)[0])

        bin_matrix, score_matrix = self.get_binary_matrices(score_type)

        with open(bin_path, 'w', newline='') as bin_file:
            bin_writer = csv.writer(bin_file)
            for row in bin_matrix:
                bin_writer.writerow(row)

        with open(s_path, 'w', newline='') as s_file:
            s_writer = csv.writer(s_file)
            for row in score_matrix:
                s_writer.writerow(row)

    def get_power_rankings(self, score_type):
        bin_matrix, score_matrix = self.get_binary_matrices(score_type)

        ib_matrix = bin_matrix.T * bin_matrix
        is_matrix = bin_matrix.T * score_matrix
        power_rankings = ib_matrix.I * is_matrix

        all_teams = self.get_sorted_team_list()
        num_teams = len(all_teams)
        all_teams = np.array(all_teams, dtype=int).reshape(num_teams, 1)
        power_rankings = np.array(power_rankings, dtype=float).reshape(num_teams, 1)
        final_list = np.hstack((all_teams, power_rankings))

        return final_list

    def export_power_rankings(self, score_type, path=None):
        pow_ranks = self.get_power_rankings(score_type)
        if not path:
            path = "data/" + self.event + "/" + self.event + "_" + score_type + "_pr.csv"
        if not os.path.exists(path.rsplit("/", 1)[0]):
            os.makedirs(path.rsplit("/", 1)[0])

        with open(path, 'w', newline='') as file:
            writer = csv.writer(file)
            for row in pow_ranks:
                writer.writerow(row)


def get_event_data(events):
    payload = {"X-TBA-Auth-Key": config.tba_api_key}
    match_entries = MatchEntryList(events)

    for event in events:
        request_url = tba_base_url + "event/" + event + "/matches"
        request = requests.get(request_url, params=payload)

        for match in request.json():
            if match["comp_level"] == "qm":
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

    match_entries.export_as_csv(path="data/world/matches.csv")
    return match_entries


def get_completed_events(year):
    current_date = date.today()

    request_url = tba_base_url + "events/" + str(year) + "/simple"
    payload = {"X-TBA-Auth-Key": config.tba_api_key}
    request = requests.get(request_url, params=payload).json()

    all_events = []
    for event in request:
        event_end_date = datetime.strptime(event["end_date"], "%Y-%m-%d").date()
        if event_end_date < current_date and 0 <= event["event_type"] <= 6:
            all_events.append(event["key"])

    return all_events


if __name__ == "__main__":
    # events = ["2018ctwat", "2018ctsct", "2018mawor", "2018nhgrs", "2018mabri", "2018marea"]
    events = get_completed_events(2018)
    entries = get_event_data(events)
    print("Got data")
    entries.export_power_rankings("total", path="data/world/total.csv")
    print("Exported OPR")
    entries.export_power_rankings("vault", path="data/world/vault.csv")
    print("Exported VPR")
    entries.export_power_rankings("foul", path="data/world/foul.csv")
    print("Exported FPR")
    # for event in events:
    #     entries = get_event_data([event])
    #     entries.export_power_rankings("foul")
    #     entries.export_power_rankings("vault")
    #     entries.export_power_rankings("total")
