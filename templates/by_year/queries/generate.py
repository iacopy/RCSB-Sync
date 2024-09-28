"""
This script generates the queries for each year,
based on the template.txt file.
"""

# Standard Library
import datetime
import os

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "template.txt"), encoding="utf-8") as file:
    template = file.read()

START_YEAR = 1975
CURRENT_YEAR = datetime.datetime.now().year

for year in range(START_YEAR, CURRENT_YEAR + 1):
    output = template.replace("$YEAR", str(year))

    FILENAME = f"Homo_sapiens__{year}.json"
    filepath = os.path.join(HERE, FILENAME)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(output)
