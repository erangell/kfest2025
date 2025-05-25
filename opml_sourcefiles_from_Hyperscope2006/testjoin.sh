python3 -m venv opml
source opml/bin/activate
python3 csv_join_script.py $1index.csv $1lines.csv $1join.csv
deactivate
