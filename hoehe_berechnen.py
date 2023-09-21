#!/usr/bin/python3

import csv
import math
from psychro import psych

#Dateinamen bitte NICHT ändern, sind hardgecodet! Stattdessen lieber Dateien umbennenen. Dateien sind nach ihrer Messmethode benannt. Daten liegen für jede Höhe als Zeile und für jede Messung als Spalte vor. Sonderfall Aßmann: Werte liegen in Trocken,Feucht,Trocken,Feucht, ... vor
#wenn keine Messung mit phyphox möglich sein sollte, phyphox aus der Liste streichen
dateinamen = ["ptb100a", "dosenbarometer", "assmann", "phyphox", "digitalbarometer", "aneroidbarometer"]

sigmas = {}
durchschnitte = {}
verarbeiteteDruecke = {}
feuchtTemperaturen = []
trockenTemperaturen = []

hoehenUnterschiedeUntenOben = {}
hoehenUnterschiedePfoertnerUnten = {}

#Umrechnung in hPa
def mmHgNachHpa(mmhg):
    return mmhg / 0.7501

def spannungNachHpa(spannung):
    return 800 + ((260/5) * spannung)

#berechnen der virtuellen Temperatur aus der Trockentemperatur und dem Mischungsverhältnis, baromet. Höhenformel
def virtuelleTemperatur(temperatur, dampfdruck, druck):
    return temperatur / (1 - ((dampfdruck / 100) / druck) * (1 - 0.622))

def barometrischeHoehenformel(druckOben, druckUnten, virtuelleTemperaturOben, virtuelleTemperaturUnten):
    return -(math.log(druckOben/druckUnten) * (287.058 * ((virtuelleTemperaturOben + 273.15) + (virtuelleTemperaturUnten + 273.15)) / 2) / 9.80665)

def dHNachdPu(virtuelleTemperaturOben, virtuelleTemperaturUnten, po):
    return -(287.058 * (((virtuelleTemperaturOben + 273.15) + (virtuelleTemperaturUnten + 273.15))/2) / (9.80665 * po))

def dHNachdPo(virtuelleTemperaturOben, virtuelleTemperaturUnten, pu):
    return -(287.058 * (((virtuelleTemperaturOben + 273.15) + (virtuelleTemperaturUnten + 273.15))/2) / (9.80665 * pu))

def dHNachdTv(po, pu):
    return -math.log(po/pu)

#statistische Funktionen
def durchschnittBerechnen(zeile):
    zaehler = 0
    summe = 0
    for element in zeile:
        zaehler = zaehler + 1
        summe = summe + element
    return summe / zaehler

def sigmaBerechnen(zeile, durchschnitt):
    fehlerQuadrat = 0
    zaehler = 0
    for element in zeile:
        zaehler = zaehler + 1
        fehlerQuadrat = (element - durchschnitt) * (element - durchschnitt)
    varianz = fehlerQuadrat / (zaehler - 1)
    return math.sqrt(varianz)

#Fehlerrechnung
def fehlerBerechnen(virtuelleTemperaturOben, virtuelleTemperaturUnten, po, pu, dTvo, dTvu, dPo, dPu):
    return math.sqrt((dHNachdPo(virtuelleTemperaturOben, virtuelleTemperaturUnten, pu) * dPo)**2 + (dHNachdPu(virtuelleTemperaturOben, virtuelleTemperaturUnten, po) * dPu)**2 + (dHNachdTv(po, pu) * (((virtuelleTemperaturOben + 273.15) + (virtuelleTemperaturUnten + 273.15)) / 2))**2)

for datei in dateinamen:
    varianzen = {}
    with open(datei + ".csv") as csvdatei:
        csvEingelesenRaw = csv.reader(csvdatei, delimiter=",")
        csvEingelesen = []

        for zeile in csvEingelesenRaw:
            csvEingelesen.append(zeile)
        
        for zeilenindex in range(len(csvEingelesen)):
            for reihenindex in range(len((csvEingelesen[zeilenindex]))):
                if (datei == "dosenbarometer") or (datei == "aneroidbarometer"):
                    csvEingelesen[zeilenindex][reihenindex] = mmHgNachHpa(float(csvEingelesen[zeilenindex][reihenindex]))
                if datei == "phyphox" or datei == "digitalbarometer":
                    csvEingelesen[zeilenindex][reihenindex] = float(csvEingelesen[zeilenindex][reihenindex])
                if datei == "ptb100a":
                    csvEingelesen[zeilenindex][reihenindex] = spannungNachHpa(float(csvEingelesen[zeilenindex][reihenindex]))

        durchschnittZeilen = []
        sigmaZeilen = []
        for zeilenindex in range(len(csvEingelesen)):
            if not (datei == "assmann"):
                durchschnitt = durchschnittBerechnen(csvEingelesen[zeilenindex])
                durchschnittZeilen.append(durchschnitt)
                sigma = sigmaBerechnen(csvEingelesen[zeilenindex], durchschnitt)
                sigmaZeilen.append(sigma)
            if datei == "assmann":
                liste_trocken = []
                liste_feucht = []
                for reihenindex in range(len(csvEingelesen[zeilenindex])):
                    if reihenindex % 2 == 0:
                        liste_trocken.append(float(csvEingelesen[zeilenindex][reihenindex]))
                    if reihenindex % 2 == 1:
                        liste_feucht.append(float(csvEingelesen[zeilenindex][reihenindex]))
                trockenTemperaturen.append(liste_trocken)
                feuchtTemperaturen.append(liste_feucht)

        if not (datei == "assmann"):
            durchschnitte[datei] = durchschnittZeilen
            sigmas[datei] = sigmaZeilen

    verarbeiteteDruecke[datei] = csvEingelesen

for datei in durchschnitte: #die Sigmas müssen wir nicht gesondert überprüfen, da sie die gleichen Keys aufweist
    #Jetzt berechnen wir die Höhenunterschiede, erst von Unten nach Oben, dann vom Pförtner nach Oben, aufgeschlüsselt nach Messmethode
    
    #erstmal für oben, dann für mitte, dann für unten
    virtuelleTemperaturen = []
    for index in range(3):
        druck_durchschnitt = durchschnitte[datei][index]
   
        virtuelleTemperaturenReihe = []
        for index_temperatur in range(len(liste_trocken)):
            virtuelleTemperaturenReihe.append(virtuelleTemperatur(trockenTemperaturen[index][index_temperatur], psych(druck_durchschnitt, "Tdb", trockenTemperaturen[index][index_temperatur], "Twb", feuchtTemperaturen[index][index_temperatur], "WVP", "SI"), druck_durchschnitt))
        virtuelleTemperaturDurchschnitt = durchschnittBerechnen(virtuelleTemperaturenReihe)
        virtuelleTemperaturSigma = sigmaBerechnen(virtuelleTemperaturenReihe, virtuelleTemperaturDurchschnitt)

        virtuelleTemperaturen.append([virtuelleTemperaturDurchschnitt, virtuelleTemperaturSigma])

    hoeheObenUnten = barometrischeHoehenformel(durchschnitte[datei][0], durchschnitte[datei][1], virtuelleTemperaturen[0][0], virtuelleTemperaturen[1][0])
    hoeheUntenPfoertner = barometrischeHoehenformel(durchschnitte[datei][1], durchschnitte[datei][2], virtuelleTemperaturen[1][0], virtuelleTemperaturen[2][0])
    fehlerObenUnten = fehlerBerechnen(virtuelleTemperaturen[0][0], virtuelleTemperaturen[1][0], durchschnitte[datei][0], durchschnitte[datei][1], virtuelleTemperaturen[0][1], virtuelleTemperaturen[1][1], sigmas[datei][0], sigmas[datei][1])
    fehlerUntenPfoertner = fehlerBerechnen(virtuelleTemperaturen[1][0], virtuelleTemperaturen[2][0], durchschnitte[datei][1], durchschnitte[datei][2], virtuelleTemperaturen[1][1], virtuelleTemperaturen[2][1], sigmas[datei][1], sigmas[datei][2])

    print("=====================================")
    print(datei)
    print("(" + str(hoeheObenUnten) + " ± " + str(fehlerObenUnten) + ")m")
    print("(" + str(hoeheUntenPfoertner) + " ± " + str(fehlerUntenPfoertner) + ")m")
