"""
This script generates the queries for each year,
based on the template.txt file.
"""
import datetime
import os

HERE = os.path.dirname(os.path.abspath(__file__))

template = open(os.path.join(HERE, "template.txt")).read()

start_year = 1970
current_year = datetime.datetime.now().year

for year in range(start_year, current_year + 1):
    output = template.replace("$YEAR", str(year))

    filename = f"Homo_sapiens__{year}.json"
    filepath = os.path.join(HERE, filename)
    with open(filepath, "w") as f:
        f.write(output)
