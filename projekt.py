import re
import numpy as np
from sympy import Matrix, lcm
import tkinter as tk
from tkinter import messagebox

def anzahl_elemente(substanz, element):
    pattern = re.compile(r'({})\d*'.format(element))
    matches = pattern.findall(substanz)
    count = 0
    for match in matches:
        num = re.search(r'\d+$', match)
        if num:
            count += int(num.group())
        else:
            count += 1
    return count

def reaktionsgleichung(reaktion):
    if "->" in reaktion:
        reaktants, produkts = reaktion.split("->")
    elif "=" in reaktion:
        reaktants, produkts = reaktion.split("=")
    else:
        return "Bitte geben Sie eine gültige chemische Gleichung mit '->' oder '=' ein."

    def substanzentren(teil):
        substanzen = {}
        verbindungen = teil.split("+")
        for verbindung in verbindungen:
            verbindung = verbindung.strip()
            match = re.match(r"(\d*)\s*([A-Za-z0-9]+)", verbindung)
            if match:
                koeffizient = int(match.group(1)) if match.group(1) else 1
                substanz = match.group(2)
                substanzen[substanz] = koeffizient
        return substanzen

    edukte_dict = substanzentren(reaktants)
    produkte_dict = substanzentren(produkts)

    elemente = set()
    for substanz in list(edukte_dict.keys()) + list(produkte_dict.keys()):
        for element in re.findall(r'[A-Z][a-z]*\d*', substanz):
            elemente.add(re.sub(r'\d', '', element))
    elemente = list(elemente)

    matrix = []
    for element in elemente:
        zeile = []
        for substanz in edukte_dict:
            zeile.append(anzahl_elemente(substanz, element))
        for substanz in produkte_dict:
            zeile.append(-anzahl_elemente(substanz, element))
        matrix.append(zeile)

    matrix = Matrix(matrix)
    loesung = matrix.nullspace()[0]
    faktor = lcm([val.q for val in loesung])
    loesung = [int(val * faktor) for val in loesung]

    koeffizienten_reaktanten = loesung[:len(edukte_dict)]
    koeffizienten_produkte = loesung[len(edukte_dict):]

    def richtige_gleichung(substanzen, koeffizienten):
        gleichung = []
        for substanz, koeffizient in zip(substanzen, koeffizienten):
            if koeffizient != 1:
                gleichung.append(f"{koeffizient}{substanz}")
            else:
                gleichung.append(substanz)
        return " + ".join(gleichung)

    reaktanten_gleichung = richtige_gleichung(edukte_dict.keys(), koeffizienten_reaktanten)
    produkte_gleichung = richtige_gleichung(produkte_dict.keys(), koeffizienten_produkte)

    ausgeglichene_gleichung = f"{reaktanten_gleichung} -> {produkte_gleichung}"

    ergebnis = "Edukte: \n"
    for substanz, koeffizient in zip(edukte_dict.keys(), koeffizienten_reaktanten):
        ergebnis += f"  {substanz}: {koeffizient}\n"

    ergebnis += "\nProdukte:\n"
    for substanz, koeffizient in zip(produkte_dict.keys(), koeffizienten_produkte):
        ergebnis += f"  {substanz}: {koeffizient}\n"

    ergebnis += f"\nAusgeglichene Gleichung:\n{ausgeglichene_gleichung}"

    return ergebnis

def anzahl_elemente(substanz, element):

    pattern = re.compile(rf'({element}\d*)')
    matches = pattern.findall(substanz)
    if not matches:
        return 0
    anzahl = 0
    for match in matches:
        if match == element:
            anzahl += 1
        else:
            anzahl += int(match[len(element):])
    return anzahl


# GUI
def on_balance():
    reaktion = entry.get()
    try:
        result = reaktionsgleichung(reaktion)
        messagebox.showinfo("Ergebnis", result)
    except Exception as e:
        messagebox.showerror("Fehler", str(e))

root = tk.Tk()
root.title("stöchiometrischer Koeffizienten bestimmen")

label = tk.Label(root, text="Geben Sie die Reaktionsgleichung ein:")
label.pack()

entry = tk.Entry(root, width=50)
entry.pack()

button = tk.Button(root, text="Gleichung ausgleichen", command=on_balance)
button.pack()

root.mainloop()
