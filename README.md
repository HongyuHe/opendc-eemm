# OpenDC EEMM

**OpenDC Extension for Energy Modelling & Management**

![version](https://img.shields.io/badge/version-0.0.1-blue) [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) [![doc](https://readthedocs.org/projects/opendc-eemm/badge/?version=latest)](https://opendc-eemm.readthedocs.io/en/latest/?badge=latest) [![travis](https://img.shields.io/travis/hongyuhe/opendc-eemm.svg)](https://travis-ci.com/hongyuhe/opendc-eemm) [![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/hongyuhe/opendc-eemm/graphs/commit-activity)[![Percentage of issues still open](http://isitmaintained.com/badge/open/Naereen/badges.svg)](http://isitmaintained.com/project/Naereen/badges "Percentage of issues still open") [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

<!-- [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) -->


![pypi](https://img.shields.io/pypi/v/opendc_eemm.svg)

[![Info](https://img.shields.io/badge/Project-Info-blue?style=flat-square&logo=data:image/svg%2bxml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iaXNvLTg4NTktMSI/Pg0KPCEtLSBHZW5lcmF0b3I6IEFkb2JlIElsbHVzdHJhdG9yIDE5LjAuMCwgU1ZHIEV4cG9ydCBQbHVnLUluIC4gU1ZHIFZlcnNpb246IDYuMDAgQnVpbGQgMCkgIC0tPg0KPHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJDYXBhXzEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHg9IjBweCIgeT0iMHB4Ig0KCSB2aWV3Qm94PSIwIDAgNTEyIDUxMiIgc3R5bGU9ImVuYWJsZS1iYWNrZ3JvdW5kOm5ldyAwIDAgNTEyIDUxMjsiIHhtbDpzcGFjZT0icHJlc2VydmUiPg0KPHBhdGggc3R5bGU9ImZpbGw6IzBBNEVBRjsiIGQ9Ik0yNTYsNTEyYy02OC4zOCwwLTEzMi42NjctMjYuNjI5LTE4MS4wMi03NC45OEMyNi42MjksMzg4LjY2NywwLDMyNC4zOCwwLDI1Ng0KCVMyNi42MjksMTIzLjMzMyw3NC45OCw3NC45OEMxMjMuMzMzLDI2LjYyOSwxODcuNjIsMCwyNTYsMHMxMzIuNjY3LDI2LjYyOSwxODEuMDIsNzQuOThDNDg1LjM3MSwxMjMuMzMzLDUxMiwxODcuNjIsNTEyLDI1Ng0KCXMtMjYuNjI5LDEzMi42NjctNzQuOTgsMTgxLjAyQzM4OC42NjcsNDg1LjM3MSwzMjQuMzgsNTEyLDI1Niw1MTJ6Ii8+DQo8cGF0aCBzdHlsZT0iZmlsbDojMDYzRThCOyIgZD0iTTQzNy4wMiw3NC45OEMzODguNjY3LDI2LjYyOSwzMjQuMzgsMCwyNTYsMHY1MTJjNjguMzgsMCwxMzIuNjY3LTI2LjYyOSwxODEuMDItNzQuOTgNCglDNDg1LjM3MSwzODguNjY3LDUxMiwzMjQuMzgsNTEyLDI1NlM0ODUuMzcxLDEyMy4zMzMsNDM3LjAyLDc0Ljk4eiIvPg0KPHBhdGggc3R5bGU9ImZpbGw6I0ZGRkZGRjsiIGQ9Ik0yNTYsMTg1Yy0zMC4zMjcsMC01NS0yNC42NzMtNTUtNTVzMjQuNjczLTU1LDU1LTU1czU1LDI0LjY3Myw1NSw1NVMyODYuMzI3LDE4NSwyNTYsMTg1eiBNMzAxLDM5NQ0KCVYyMTVIMTkxdjMwaDMwdjE1MGgtMzB2MzBoMTQwdi0zMEgzMDF6Ii8+DQo8Zz4NCgk8cGF0aCBzdHlsZT0iZmlsbDojQ0NFRkZGOyIgZD0iTTI1NiwxODVjMzAuMzI3LDAsNTUtMjQuNjczLDU1LTU1cy0yNC42NzMtNTUtNTUtNTVWMTg1eiIvPg0KCTxwb2x5Z29uIHN0eWxlPSJmaWxsOiNDQ0VGRkY7IiBwb2ludHM9IjMwMSwzOTUgMzAxLDIxNSAyNTYsMjE1IDI1Niw0MjUgMzMxLDQyNSAzMzEsMzk1IAkiLz4NCjwvZz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjwvc3ZnPg0K)](https://opendc-eemm.rtfd.io)

Document: <https://opendc-eemm.rtfd.io>.

---

## Usage

### Top-level commands:
```shell
usage: opendc-eemm [-v] [-h] -t path [--pue float] {trace,market,decision} ...

CLI of OpenDC Extension for Energy Modelling & Managament.

optional arguments:
  -v, --version         Show version number of the package and exit.
  -h, --help            Show the help messages and exit.
  -t path, --trace path
                        Path to simulation results (expecting a Parque file).
  --pue float           PUE value of the simulatied datacenter.

subcommands:
  Available commands.

  {trace,market,decision}
    trace               Visualize simulation results.
    market              Compare costs in different markets.
    decision            Optimize fine-grained decision-making.
```

### Visualize simulation results:

```shell
usage: opendc-eemm trace [-h] -s ['power', 'oc'] [-f float] [-g value]

optional arguments:
  -s ['power', 'oc'], --show ['power', 'oc']
                        Choose 'power' to show power draw; choose 'oc' to show over-commissioned.
  -f float, --frequency float
                        Frequency of simulated machines.
  -g value, --governor value
                        Governor to visualize.
```

### Analyze energy markets:

```shell
usage: opendc-eemm market [-h] -s ['load', 'strategy'] -o float -d path -i path

optional arguments:
  -s ['load', 'strategy'], --show ['load', 'strategy']
  -o float, --od_price float
                        On-demand energy price.
  -d path, --dayahead_prices path
                        Path to day-ahead energy prices (expecting a CSV file).
  -i path, --imbalance_prices path
                        Path to imbalance energy prices (expecting a CSV file).
```

### Invoke DVFS scheduler:

```shell
usage: opendc-eemm decision [-h] -o ['score', 'schedule'] [-f float] -d path -i path -p path -a ['first', 'last', 'mean'] [-s path]

optional arguments:
  -o ['score', 'schedule'], --option ['score', 'schedule']
                        Choose 'score' to compute the agreement accuracy (AA) sore of the predictions; choose 'schedule' for DVFS
                        scheduling.
  -f float, --factor float
                        Damping factor of the DVFS scheduler.
  -d path, --dayahead_prices path
                        Path to day-ahead energy prices (expecting a CSV file).
  -i path, --imbalance_prices path
                        Path to imbalance energy prices (expecting a CSV file).
  -p path, --predictions path
                        Machine learning predictions (expecting a CSV file).
  -a ['first', 'last', 'mean'], --aggregate ['first', 'last', 'mean']
                        Aggregation method for machine learning predictions.
  -s path, --save_to path
                        Destination path of the DVFS schedule.
```
