"""
Load a file containing valid student usernames/crsids convert these to anonymzed values 
"""
import csv
import sys


def anonymize_selection_file(filename):
    """
    Convert student names and crsids to anonymous values

    We could convert the supervisor crsid but slightly more complex as we need to store a lookup
    """
    

    rows = 0

    with open(filename, newline='', encoding='utf8') as csvfile, open('anon_'+filename, 'w', newline='') as outfile:

        selectionreader = csv.reader(csvfile, delimiter=',', quotechar='"')

        spamwriter = csv.writer(outfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for row in selectionreader:
            rows += 1
            if rows != 1:
            # TODO: test exists already?
                row[0] = "stu"+str(rows)
                row[1] = "firstname"+str(rows)
                row[2] = "lastname"+str(rows)


            spamwriter.writerow(row)
            selectionreader = csv.reader(csvfile, delimiter=',', quotechar='"')



if len(sys.argv) != 2:
    print(f"usage: {sys.argv[0]} <filename>")
else:
    anonymize_selection_file(sys.argv[1])
