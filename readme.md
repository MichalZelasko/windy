# Installation

W celu instalacji aplikacji należy pobrać kod z serwisu github (w postaci archiwum ZIP), a następnie lokalnie rozpakować.

![alt text](./documentation/download.png)

Alternatywnie można pobrać zawartość całego repozytorium za pomocą linii komend wykorzystując polecenie:

'''
gh repo clone MichalZelasko/windy
'''

## Requirements

Oprogramowanie zostało napisane w pythonie, dlatego niezbędne jest zainstalowanie na komputerze aktualnej wesji interpretera. Kolejnym krokiem niezbędnym do uruchomienia aplikacji jest instalacja/uaktualnienie bibliotek. 

'''
pip install -r requirements.txt
'''

## Running

Aplikację można uruchomić po przejściu do katalogu ./code z pomocą polecenia:

'''
python app.py
'''

# Description

Celem aplikacji jest umożliwienie prowadzenia predykcji rozwoju chmur burzowych na podstawie danych z radaru opadów ze strony: https://www.windy.com. Program pobiera dane ze wskazanego adresu url (mapa reprezentująca aktualne opady na wybranym obszarze) na podstawie, których uzyskiwane są informacje o położeniu, obszarze i intensywności opadów w ciągu ostatniej godziny (w postaci map opadów dla kilku kroków czasowych).

![alt text](./documentation/example_screenshot.png)

W kolejnym etapie następuje podział opadów na klastry (chmury, komórki burzowe) dla ktorych określane jest ich dokładne położenie, rozmiar i intensywność opadów. Wykonanie takiego podziału dla każdego zdjęcia pozwala okreslić historię rozwoju opadów. 

![alt text](./output/clusters.png)

Na podstawie zebranych informacji ekstrapolowana jest zmiana położenia, rozmiaru i intensywności opadów w poszczególnych chmurach. Aplikacja następnie dokonuje wizualizacji wykonanych predykcji (w postaci animacji w formacie .gif i wykresów przedstawiających wartości poszczególnych cech charaktestycznych klastrów). W celu uzyskania realistycznego tła dla animacji należy wskazać również adres url strony internetowej z mapą stanowiącą tło.

![Alt Text](./output/animation_2.gif)

Do sterowania parametrami klasteryzacji, ekstrapolacji i wizualizacji wykorzystywany jest plik konfiguracyjny. Umożliwia to między innymi wybór metody klasteryzacji i ekstrapolacji (szczegóły w sekcji **Configuration**).
## Screenshoter

## Converter

## Cloud extraction

## Clusterizer

### Methods

## Extrapolation

### Methods

## Animation

# Configuration