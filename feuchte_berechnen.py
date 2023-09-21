#Aßmann und Falkenberger
#Ablesefehler der Temp +-0.2 Grad, Falkenberger +-0.1 Grad

from psychropy import psych
import numpy as np
import matplotlib.pyplot as plt
import math
import csv

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

relative_luftfeuchtigkeiten = {}
fehler_luftfeuchtigkeiten = {}
trockentemperaturen = {}
feuchttemperaturen = {}

trockentemperatur_geeicht = 0
trockentemperatur_geeicht_abweichung = 0

def taupunktR(rf, dttv):
    return psych(101325, "Tdb", trockentemperatur_geeicht + (dttv * trockentemperatur_geeicht_abweichung), "RH", rf, "DP", "SI")
    
def absfeuchteR(rf, dttv):
    return psych(101325, "Tdb", trockentemperatur_geeicht + (dttv * trockentemperatur_geeicht_abweichung), "RH", rf, "W", "SI")
    
def rfR(tp, dttv):
    return psych(101325, "Tdb", trockentemperatur_geeicht + (dttv * trockentemperatur_geeicht_abweichung), "DP", tp, "RH", "SI")
    
def mischungsverhaeltnisR(tp, dttv):
    print(rf)
    return psych(101325, "Tdb", trockentemperatur_geeicht + (dttv * trockentemperatur_geeicht_abweichung), "W", tp, "DSat", "SI")
    
def taupunkt(rf, drf):
    return [taupunktR(rf, 0), max(abs(taupunktR(rf, 0) - taupunktR(rf + drf, -1)), abs(taupunktR(rf, 0) - taupunktR(rf - drf, 1)))]
    
def absfeuchte(rf, drf):
    return [absfeuchteR(rf, 0), max(abs(absfeuchteR(rf, 0) - absfeuchteR(rf - drf, 1)), abs(absfeuchteR(rf, 0) - absfeuchteR(rf + drf, -1)))]
    
def rf(tp, dtp):
    return [rfR(tp, 0), max(abs(rfR(tp, 0) - rfR(tp - dtp, 1)), abs(rfR(tp, 0) - rfR(tp + dtp, -1)))]
    
def mischungsverhaeltnis(rf, drf):
    return [mischungsverhaeltnisR(rf, 0), max(abs(mischungsverhaeltnisR(rf, 0) - mischungsverhaeltnisR(rf - drf, 1)), abs(mischungsverhaeltnisR(rf, 0) - mischungsverhaeltnisR(rf + drf, -1)))]

max_t = 100000
def druckikovski(dateiname, plotzaehler, titel):
    global max_t
    T_f = []
    T_t = []

    dateiRaw = csv.reader(open(dateiname), delimiter=",")
    
    for zeile in dateiRaw:
        T_t.append(float(zeile[0]))
        T_f.append(float(zeile[1]))
    
    t=[]
    zaehler = 0
    zeitintervall = 5 #5 Sekunden
    for i in range(len(T_t)):
        t.append(zaehler * zeitintervall)
        zaehler = zaehler + 1
    max_t = min(len(t), max_t)
    e=[]
    ungenau = 0.2
    for i in range(len(t)):
        if titel == "Frankenberger":
            ungenau = 0.1
        e.append(ungenau)
    plt.figure(plotzaehler)
    plt.title(titel)
    plt.plot(t, T_f,'o',color='green',label="Feuchttemperatur")
    plt.plot(t, T_t, 'o',color='blue',label="Trockentemperatur")
    plt.errorbar(t,T_f,e,ecolor='green', linestyle='')
    plt.errorbar(t,T_t,e,ecolor='blue', linestyle='')
    plt.ylabel("Temperatur in °C")
    plt.xlabel("Zeit in s")
    plt.legend()
    plt.grid(True)
    plt.show()
    
    relative_luftfeuchtigkeiten[plotzaehler] = []
    fehler_luftfeuchtigkeiten[plotzaehler] = []
    for index in range(len(T_t)):
        relative_luftfeuchtigkeiten[plotzaehler].append(psych(101300, "Tdb", T_t[index], "Twb", T_f[index], "RH", "SI"))
        fehler_oben = abs(psych(101300, "Tdb", T_t[index], "Twb", T_f[index], "RH", "SI") - psych(101300, "Tdb", T_t[index] - ungenau, "Twb", T_f[index] + ungenau, "RH", "SI"))
        fehler_unten = abs(psych(101300, "Tdb", T_t[index], "Twb", T_f[index], "RH", "SI") - psych(101300, "Tdb", T_t[index] + ungenau, "Twb", T_f[index] - ungenau, "RH", "SI"))
        fehler_luftfeuchtigkeiten[plotzaehler].append(max(fehler_oben, fehler_unten))
    trockentemperaturen[plotzaehler] = [durchschnittBerechnen(T_t), sigmaBerechnen(T_t, durchschnittBerechnen(T_t)), ungenau]
    feuchttemperaturen[plotzaehler] = [durchschnittBerechnen(T_f), sigmaBerechnen(T_f, durchschnittBerechnen(T_f)), ungenau]

druckikovski("/home/alexander/instrumentenpraktikum/luftfeuchtigkeit/assmann.csv", 0, "Aßmann")
druckikovski("/home/alexander/instrumentenpraktikum/luftfeuchtigkeit/falkenberger.csv", 1, "Frankenberger")

trockentemperatur_geeicht = trockentemperaturen[1][0]
trockentemperatur_geeicht_abweichung = trockentemperaturen[1][1]

taupunkte = {}

print("==========================")
print("Aßmann")
mue = durchschnittBerechnen(relative_luftfeuchtigkeiten[0])
sig = sigmaBerechnen(relative_luftfeuchtigkeiten[0], mue)
print("(" + str(mue * 100) + " ± " + str(sig * 100) + ")% relative Luftfeuchtigkeit")
#das ist irgendwie eine Frickelei
tp = psych(101300, "Tdb", trockentemperaturen[0][0], "RH", mue, "DP", "SI")
tp_max = psych(101300, "Tdb", trockentemperaturen[0][0] - trockentemperaturen[0][2], "RH", mue + sig, "DP", "SI")
tp_min = psych(101300, "Tdb", trockentemperaturen[0][0] + trockentemperaturen[0][2], "RH", mue - sig, "DP", "SI")
tp_abw = max(abs(tp - tp_max), abs(tp - tp_min))
taupunkte[0] = [tp, tp_abw]
print("Entspricht einem Taupunkt von")
print("(" + str(tp) + " ± " + str(tp_abw) + ")°C")
print("Trockentemperatur bestimmt als:")
print("(" + str(trockentemperaturen[0][0]) + " ± " + str(trockentemperaturen[0][1]) + ")°C")
print("Feuchttemperatur bestimmt als:")
print("(" + str(feuchttemperaturen[0][0]) + " ± " + str(feuchttemperaturen[0][1]) + ")°C")
print(absfeuchte(mue, sig))
print(mischungsverhaeltnis(absfeuchte(mue, sig)[0], absfeuchte(mue,sig)[1]))

print ("=========================")
print("Frankenberger")
mue = durchschnittBerechnen(relative_luftfeuchtigkeiten[1])
sig = sigmaBerechnen(relative_luftfeuchtigkeiten[1], mue)
print("(" + str(mue * 100) + " ± " + str(sig * 100) + ")% relative Luftfeuchtigkeit")
tp = psych(101300, "Tdb", trockentemperaturen[1][0], "RH", mue, "DP", "SI")
tp_max = psych(101300, "Tdb", trockentemperaturen[1][0] - trockentemperaturen[1][2], "RH", mue + sig, "DP", "SI")
tp_min = psych(101300, "Tdb", trockentemperaturen[1][0] + trockentemperaturen[1][2], "RH", mue - sig, "DP", "SI")
tp_abw = max(abs(tp - tp_max), abs(tp - tp_min))
taupunkte[1] = [tp, tp_abw]
print("Entspricht einem Taupunkt von")
print("(" + str(tp) + " ± " + str(tp_abw) + ")°C")
print("Trockentemperatur bestimmt als:")
print("(" + str(trockentemperaturen[1][0]) + " ± " + str(trockentemperaturen[1][1]) + ")°C")
print("Feuchttemperatur bestimmt als:")
print("(" + str(feuchttemperaturen[1][0]) + " ± " + str(feuchttemperaturen[1][1]) + ")°C")
print(absfeuchte(mue, sig))
print(mischungsverhaeltnis(absfeuchte(mue, sig)[0], absfeuchte(mue,sig)[1]))

t = []
zaehler = 0
for i in range(max_t):
    t.append(5 * zaehler)
    zaehler = zaehler + 1
    
def hundert(zahl):
    return zahl * 100
    
plt.figure(2)
plt.title("Relative Luftfeuchtigkeiten")
plt.plot(t, list(map(hundert, relative_luftfeuchtigkeiten[0][:len(t)])),'o',color='green',label="Aßmann")
plt.plot(t, list(map(hundert, relative_luftfeuchtigkeiten[1][:len(t)])), 'o',color='blue',label="Falkenberger")
plt.errorbar(t,list(map(hundert, relative_luftfeuchtigkeiten[0][:len(t)])),list(map(hundert, fehler_luftfeuchtigkeiten[0][:len(t)])),ecolor='green', linestyle='')
plt.errorbar(t,list(map(hundert, relative_luftfeuchtigkeiten[1][:len(t)])),list(map(hundert, fehler_luftfeuchtigkeiten[0][:len(t)])),ecolor='blue', linestyle='')
plt.ylabel("Relative Luftfeuchtigkeit in Prozent")
plt.xlabel("Zeit in s")
plt.legend()
plt.grid(True)
plt.show()

def durchHundert(zahl):
    return zahl / 100

def tauspieglikovski(dateipfad, name):
    dateiRaw = csv.reader(open(dateipfad), delimiter=",")
    taupunkttemperaturen = []
    for zeile in dateiRaw:
        taupunkttemperaturen.append(float(zeile[0]))
    
    rh_von_taupunkt = psych(101300, "Tdb", 21.3, "DP", durchschnittBerechnen(taupunkttemperaturen), "RH", "SI")
    
    print("===============================================")
    print(name)
    print("(" + str(durchschnittBerechnen(taupunkttemperaturen)) + " ± " + str(sigmaBerechnen(taupunkttemperaturen, durchschnittBerechnen(taupunkttemperaturen))) + ")°C")
    if name == "Taupunktspiegel":
        rawdata = rf(durchschnittBerechnen(taupunkttemperaturen), sigmaBerechnen(taupunkttemperaturen, durchschnittBerechnen(taupunkttemperaturen)))
        mue = rawdata[0]
        sig = rawdata[1]
        print(rawdata)
    if name == "Haarhygrometer":
        mue = durchschnittBerechnen(list(map(durchHundert, taupunkttemperaturen)))
        sig = sigmaBerechnen(list(map(durchHundert, taupunkttemperaturen)), mue)
        print(taupunkt(mue, sig))
    print(absfeuchte(mue, sig))
    print(mischungsverhaeltnis(absfeuchte(mue, sig)[0], absfeuchte(mue, sig)[1]))
    
tauspieglikovski("/home/alexander/instrumentenpraktikum/luftfeuchtigkeit/taupunktspiegel.csv", "Taupunktspiegel")
tauspieglikovski("/home/alexander/instrumentenpraktikum/luftfeuchtigkeit/haarhygrometer.csv", "Haarhygrometer")

