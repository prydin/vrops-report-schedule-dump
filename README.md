# vRealize Operations Schedule Dumper
A simple utility that dumps detailed information about report schedules. This is useful mainly because the UI doesn't show the 
resource for a report. 

## Installing
```bash
git clone https://github.com/prydin/vrops-report-schedule-dump
pip install --user -r requirements.txt
```

## Usage
```
python dumpschedules.py [-h] 
  --url <vR Ops URL> 
  --user <vR Ops User> 
  --password <vR Ops password> 
  --token <API token (vR Ops Cloud only)>
  --report <report name> 
  --output <output file> 
  --format <pdf or csv>
```
Authentication is done either through username/password OR using a token (cloud only)

If no report name is specified, all reports will be dumped.

## Example
```
python dumpschedules.py --url http://myvrops.example.com --user admin --password topsecret --report "Capacity Report - Datastores" --output out.csv
```
