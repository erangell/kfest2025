python3 -m venv opml
source opml/bin/activate
python3 opml_to_csv_index.py $1.opml $1index.csv
deactivate

