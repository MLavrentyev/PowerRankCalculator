# PowerRankCalculator
A calculator to calculate OPR, Vault PR, and Foul PR for FRC. 

To run and generate data, do the following:
- run `entries = get_event_data(event)` where `event` is the event key
- run `entries.export_power_rankings(score_type, path=None)`. `score_type` is one of the following strings: "foul", "vault", "total". If `path` is not provided, the default path of `data/<event_key>/<event_key>_<score_type>_pr.csv` is used. Otherwise, the provided path is used.

For more help, see [lines 153-159](https://github.com/MLavrentyev/PowerRankCalculator/blob/44179c29b14d605b0b067e6b0fd0cf70a2befc84/main.py#L152) of `main.py`.
