python3 -m venv opml
source opml/bin/activate
python3 csv2basic.py $1join.csv $1data.txt
deactivate
