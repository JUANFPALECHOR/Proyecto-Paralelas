import csv
import os

def save_row_to_csv(filepath, row, header=None):
    file_exists = os.path.isfile(filepath)

    with open(filepath, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)

        # Si el archivo NO existe todavía, escribe el encabezado
        if not file_exists:
            writer.writeheader()

        writer.writerow(row)
