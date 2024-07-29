# Installation

W celu instalacji aplikacji należy pobrać kod z serwisu github (w postaci archiwum ZIP), a następnie lokalnie rozpakować.

![alt text](./documentation/download.png)

Alternatywnie można pobrać zawartość całego repozytorium za pomocą linii komend wykorzystując polecenie:

```
gh repo clone MichalZelasko/windy
```

## Requirements

Oprogramowanie zostało napisane w pythonie, dlatego niezbędne jest zainstalowanie na komputerze aktualnej wesji interpretera. Kolejnym krokiem niezbędnym do uruchomienia aplikacji jest instalacja/uaktualnienie bibliotek. 

```
pip install -r requirements.txt
```

## Running

Aplikację można uruchomić po przejściu do katalogu ./code z pomocą polecenia:

```
python app.py
```

# Description

Celem aplikacji jest umożliwienie prowadzenia predykcji rozwoju chmur burzowych na podstawie danych z radaru opadów ze strony: https://www.windy.com. Program pobiera dane ze wskazanego adresu url (mapa reprezentująca aktualne opady na wybranym obszarze) na podstawie, których uzyskiwane są informacje o położeniu, obszarze i intensywności opadów w ciągu ostatniej godziny (w postaci map opadów dla kilku kroków czasowych).

![alt text](./documentation/example_screenshot.png)

W kolejnym etapie następuje podział opadów na klastry (chmury, komórki burzowe) dla ktorych określane jest ich dokładne położenie, rozmiar i intensywność opadów. Wykonanie takiego podziału dla każdego zdjęcia pozwala okreslić historię rozwoju opadów. 

![alt text](./output/clusters.png)

Na podstawie zebranych informacji ekstrapolowana jest zmiana położenia, rozmiaru i intensywności opadów w poszczególnych chmurach. Aplikacja następnie dokonuje wizualizacji wykonanych predykcji (w postaci animacji w formacie .gif i wykresów przedstawiających wartości poszczególnych cech charaktestycznych klastrów). W celu uzyskania realistycznego tła dla animacji należy wskazać również adres url strony internetowej z mapą stanowiącą tło.

![Alt Text](./output/animation_2.gif)

Do sterowania parametrami klasteryzacji, ekstrapolacji i wizualizacji wykorzystywany jest plik konfiguracyjny. Umożliwia to między innymi wybór metody klasteryzacji i ekstrapolacji (szczegóły w sekcji **Configuration**).

## Screenshoter

Pierwszy etap działania aplikacji opiera się na wykonaniu screenshotów podanej w pliku konfiguracyjnym strony internetowej zawierającym mapę opadów z wykorzystaniem biblioteki Selenium (https://selenium-python.readthedocs.io/). Po uruchomieniu programu pojawi się okno przeglądarki ze stroną internetową: https://www.windy.com/pl/-Radar-pogodowy-radar?radar. Jeśli pojawi się zapytanie o akceptację plików cookie należy wybrać dowolną opcję umożliwiającą przejście do właświej strony. Aplikacja automatycznie uruchomi animację na stronie internetowej i wykona zdjęcia strony internetowej. Następnie okno przeglądarki zniknie i proces powtórzy się dla procesu pobrania tła (pustej mapy). Odpowiednie adresy internetowe należy wprowadzić w pliku konfiguracyjnym (./conf/conf.json). W pliku można również ustalić wartości opóźnień dla poszczególnych etapów procesu wykonywania zrzutów ekranu (można je modyfikować w zależności od szybkości internetu - szczegóły w sekcji **Configuration**). 

## Converter

Wykonane zdjęcia zawierają elementy strony internetowej utrudniające interpretację (logo, menu legenda), dlatego obszar zdjęcia musi zostać ograniczony (parametry tego procesu są konfigurowalne, pola: *x_a*, *x_b*, *y_a*, *y_b* w pliku konfiguracyjnym, wartości domyślne *None* oznaczają, że program automatycznie dobierze szerkość marginesów tak by usunąć niepotrzebne elementy strony internetowej). Skonwertowane pliki zostaną następnie przeniesione do wskazanego katalogu.

## Cloud extraction

W celu uzyskania danych ilościowych o intensywności opadów na podstawie map barwnych następuje usunięcie niepotrzebnych elementów ze zdjęcia (np.: symbole kamer internetowych), selekcja obszarów, na których występują opady, przeliczenie skali barwnej na intensywność opadów, usunięcie krawędzi (nazwy miast, krawędzie symboli). Na tym etapie opady reprezentowane są jako zbiór punktów posiadających współrzędne oraz przypisaną im intensywność opadów.

## Clusterizer

Kolejnym etapem jest grupowanie punktów w klastry reprezentujących strefy opadów (poszczególne chmury, komórki burzowe). Przed właściwą klasteryzacją następuje wylosowanie podzbioru punktów (z prawdopodobieństwem proporcjonalnym do intensywności opadów - wagi). Procent punktów, które znajdą się w końcowym podzbiorze można ustawić za pomocą parametru *prob* w plicku konfiguracyjnym. Pozwala to na uwzględnienie intensywności opadów przy wykrywaniu komórek burzowych i wydzielenie z dużych obszarów opadów podobszarów o zwiększonej intensywności.

### Methods

Do klasteryzacji zbioru punktów wykorzystano różne metody klasteryzacji, wyboru metody można dokonać poprzez plik konfiguracyjny:

1. KMeans - klasyczna metoda kmeans z hiperparamtrem k - reprezentującym liczbę klastrów. Do ustalenia tego parametru wykorzystywana jest metoda łokciowa (zakres badania można konfigurować za pomocą parametrów *elbow_start*, *elbow_stop*, *elbow_step*). Wyznaczona za pomocą metody łokciowej liczbę klastrów wykorzystuje się do ostatecznego podziału zbioru punktów.
![alt text](./documentation/kmeans.png)
2. DBSCAN - metoda DBSCAN z biblioteki **scikit-learn**, za pomocą pliku konfiguracyjnego można ustalić parametr *eps* (https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html).
![alt text](./documentation/dbscan.png)
3. Metoda mieszana - (opracowanie własne) metoda polegająca na uruchomieniu metody DBSCAN w celu wyznaczenia liczby i położenia centrów klastrów, które wykorzystywane są do inicjalizacji metody KMEANS.
![alt text](./documentation/mixed.png)
4. Metoda hierarchiczna - (opracowanie własne) metoda polegająca na naprzemiennym i hierarchicznym podziale zbioru zbioru danych za pomocą metod KMEANS (liczba klastrów konfigurowalna za pomocą *n_clusters*) i DBSCAN, o tym która metoda jest wykorzystywana jako pierwsza decyduje parametr *kmeans_first*. O liczbie warstw podziałów decyduje parametr *clusterize_depth*.
![alt text](./documentation/hierarchical.png)

## History of storm development
Klasteryzacja prowadzona jest dla każdej mapy, następnie dla każdego klastra wyznaczany jest jego przodek (cluster na mapie reprezentujących poprzedni krok czasowy, który leży najbliżej). Na tej podstawie powstaje graf historii rozwoju chmur.

## Extrapolation
Dla każdego klastra określane są jego atrybuty:
* współrzędne x, y,
* sumaryczna intensywność opadów w klastrze (mocy - power),
* rozmiar klastra względem kierunków (pozwala to na przybliżenie kształtu chmury za pomocą wielokątu).
Wykorzystując historię zmiany wartości cech poszczególnych klastrów (wyznaczoną po podstawie cech poprzedników w grafie historii rozwoju chmur) można dokonać ekstrapolacji wartości tych atrybutów. Dokładny zakres czasów, dla których wykonana jest ekstrapolacja można ustawić za pomocą pól *extr_stop* - koniec ekstrapolacji w minutach i *extr_step* - krok czasowy z jakim generowane będę kolejne klatki w animacji.

### Methods

Do ekstrapolacji wykorzystano następujące metody:
1. Regresja liniowa - implementacja z biblioteki scikit-learn (https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html).
2. Interpolacja barycentryczna - klasa BarycentricInterpolator z biblioteki scipy (https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.BarycentricInterpolator.html).
3. Interpolacja spline'ami - metoda make_interp_spline z biblioteki scipy (https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.make_interp_spline.html).
4. Interpolacja spline'ami kubicznymi - klasa CubicSpline z biblioteki scipy (https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.CubicSpline.html).
5. Metoda interp1d z biblioteki scipy.
6. Metody aproksymacyjne (implementacja z wykorzystaniem scipy):
    * aproksymacja funckją liniową,
    * aproksymacja funckją kwadratową,
    * aproksymacja wielomianowa,
    * aproksymacja poprzez iloraz wielomianów.

Animacja ekstrapoloacji z wykorzystaniem regresji liniowej:
![Alt Text](./output/animation_3.gif)

Animacja ekstrapoloacji z wykorzystaniem ilorazu wielomianów:
![Alt Text](./output/animation_4.gif)

## Wizualizacja i animacja

Podstawowa animacja obejmuje przedstawienie wyekstrapolowanego rozwoju opadów w postaci pliku .gif z wykorzystaniem skali barwnej *jet* z bilioteki Matplotlib. Poszczególne klatki animacji powstają poprzez naniesienie punktów wchodzących w skład klastrów (przesuniętych zgodnie z przemieszczeniem i zmianą rozmiaru klastrów). Przyjęto, że odległość danego punktu od środka ciężkości klastra zmienia się proporcjonalnie do rozmiaru klastra (przesunięcię środka klastra wynika z ekstrapolacji i ogólnej tendencji do przemieszczania się chmur, relacja pomiędzy tymi przesunięciami definiowana jest poprzez parametr *move_coeff*). Intensywność opadów w danym punkcie zależy proporcjonalnie do wyekstrapolowanej mocy klastra (power) i odwrotnie proporcjonalnie do kwadratu rozmiaru klastra (moc klastra trakujemy jako całkę do intensywności opadów, dlatego wzrost obszaru zajmowanego przez klaster musi wiązać się z odwrotnie proporcjonalnym spadkiem intensywności opadów w poszczególnych punktach). Dodatkowo wprowadzono parametr *t_ceoff* - reprezentujący tłumienie rozwoju burz w czasie (wartość 0 - oznacza, że intensywność opadu w czasie nie ulega spadkowi względem wartości wyekstrapolaowanej, wartość 1 - ozancza, że opad zanika po 100 minutach - krótkotrwały opad burzowy). Do konstruowania animacji wykorzystano bibliotekę celluloid 0.2.0 (https://github.com/jwkvam/celluloid).

Dodatkowo w ramach wizualizacji można skonfigurować możliwość tworzenia rysunków przedstawiających:
* podział wejściowych map na klastry, 
* wartości ekstrapolowanych wielkości dla poszczególnych klastrów,
* wykres zależności jakości klasteryzacji od liczby klastrów dla metody łokciowej, 
* graf skierowany (DAG) ewolucji klastrów, 
* położenie klastrów w trakcie ekstrapolacji.

# Configuration

Plik konfiguracyjny ("./conf/coonf.json") umożliwia dopasowanie parametrów sterujących działaniem aplikacji do potrzeb. Modyfikowane mogą być następujące zmienne:

* "screenshoot" - parametry konfigurujące wykonywanie zrzutów ekranu:
    - "do_screenshot": true | **false** - czy wykonywać zrzuty ekranu z portalu https://www.windy.com/pl/-Radar-pogodowy-radar?radar,
    - "url": **"https://www.windy.com/pl/-Radar-pogodowy-radar?radar,54.632,13.964,7,m:e02agSR"** - adres url, z którego pobierane są mapy opadów,
    - "url_map": **"https://www.windy.com/pl/-Fale-waves?waves,2024072615,54.632,13.964,7,i:pressure,m:e02agSR"** - adres url, z którego pobierana jest pusta mapa (tło),
    - "delay_1": int | float (default: **10**) - wartość opóźnienia, po którym następuje uruchomienie animacji na stronie internetowej od pojawienia się okna przeglądarki,
    - "delay_2": int | float (default: **4**) - wartość opóźnienia od uruchomienia animacji do wykonania pierwszego zrzutu ekranu,
    - "screenshot_number": int (default: **10**) - liczba wykonywanych zrzutów ekranu,
    - "screenshot_time": int | float (default: **7**) - czas na wykonanie wszystkich zrzutów ekranów,
    - "do_convert": true | **false** - czy wykonywać konwersję plików z katalogu *resource*.

* "filepaths" - ścieżki do plików i katalogów:
    - "resource": "../resources/raw_picture" - ścieżka do katalogu ze screenshotami strony internetowej,
    - "path": "../resources/pictures" - ścieżka do katalogu ze skonwertowanymi plikami,
    - "map": "../resources/maps/Map_tmp.png" - ścieżka do pliku zawierającego mapę stanowiącą tło animacji (rozszerzenie .png),
    - "animation": "../output/animation_4.gif" - ścieżka do pliku będącego animację przedstawiąjącą wyniki ekstrapolacji rozwoju opadów (rozszerzenie .gif).

* "picture_setting" - parametry sterujące konwertowaniem screenshotów do formy wykorzystywanej przez animację:
    - "grey_difference": int (default: **32**) - maksymalna różnica pomiędzy poszczególnymi składowymi RGB tak by piksel został oceniony jako szary (nie reprezentujący intensywności opadu),
    - "image_size": int (default: **1920**) - rozmiar obrazu,
    - "x_a": **null** | int - górny margines,
    - "x_b": **null** | int - dolny margines,
    - "y_a": **null** | int - lewy margines,
    - "y_b": **null** | int - prawy margines.

* "colormap" - parametry sterujące wykrywaniem stref opadów i określeniem ich intensywności:
    - "step_1": 20,
    - "step_2": 40,
    - "step_3": 60,
    - "half_way": 30.

* "sampling" - parametryzacja próbkowania zbioru punktów:
    - "prob": float (default: **0.1**) - ułamek liczby punktów uwzględnianych przy klasteryzacji,
    - "scale": float (default: **300**) - skala (właściwa skala oblicza jako scale / image_size).

* "cluster" - parametry sterujące procesem klasteryzacji (wykrywania strefopadów/burz):
    - "elbow_start": int (default: **2**) - najmniejsza liczba klastrów analizowana w ramach metody łokciowej,
    - "elbow_stop": int (default: **50**) - największa liczba klastrów analizowana w ramach metody łokciowej,
    - "elbow_step": int (default: **4**) - krok w metodzie łokciowej,
    - "eps_coeff": float (default: **1.41**) - współczynnik *eps* w metodzie DBSCAN,
    - "mixed_coeff": (default: **1.41**) - 1 / *mixed_coeff* oznacza ułamek (w metodzie *mixed*) liczby klastrów wskazanych przez metodę DBSCAN, za pomocą których inicjalizowana jest metoda KMeans,
    - "clusterize_depth": int (default: **4**) - głębokość drzewa w podziale na klastry za pomocą metody hierarchicznej,
    - "kmeans_first": **true** | false - przy zastosowaniu metody *hierarchical* informacja czy metoda KMeans jest wykorzystywana jako pierwsza,
    - "n_clusters": int (default: **2**) - liczba klastrów, na które dzielony jest podzbiór punktów w metodzie hierarchicznej na etapie wykorzystującym metodę KMeans,
    - "option_clust": **"mixed"** | "kmeans" | "dbscan" | "hierarchical" - metoda klasteryzacji.

* "extrapolation" - parametry sterujące procesem ekstrapolacji:
    - "option_pos": **"linear"** | "noncubic" | "slinear" | "quadratic" | "cubic" | "cubicspline" | "polynomial" | "aproximation" - sposób ekstrapolacji pozycji środków ciężkości klastrów, 
    - "option": **"linear"** | "noncubic" | "cubicspline" | "polynomial" | "aproximation" - sposób ekstrapolacji siły (power) klastrów i ich rozmiaru, 
    - "k": int (default: **3**) - przybliżenie przy ekstrapolacji z pomocą rozwinięcia w szereg Taylora, 
    - "func": **"hyperbolic"** | "linear" | "square" | "polynomial" | "division" | "taylor" - rodzaj funkcji wykorzystywanej przy wybraniu opcji *aproximation*,
    - "extr_stop": int (default: **60**) - maksymalny czas, dla którego wykonywana jest ekstrapolocja,
    - "extr_step": int (default: **2**) - krok czasowy - co ile minut wykonywana jest mapa przedstawiająca ekstrapolację opadów.

* "visualization" - parametry sterujące procesem wizualizacji:
    - "do_draw_clusters": true | **false** - czy wizualizować klastry na mapach wejściowych,
    - "do_draw_elbow_graph": true | **false** - czy pokazać wykres przedstawiający jakość klasteryzacji w metodzie łokciowej,
    - "do_draw_graph": true | **false** - czy wizualizować graf relacji pomiędzy klastrami,
    - "do_draw_cluster_centers": true | **false** - czy nanosić na mapę ekstrapolacji położenia klastrów,
    - "do_plot_extrapolation": true | **false** - czy wizualizować w postaci wykresów wyniki ekstrpolacji (cechy poszczególnych klastrów),
    - "move_coeff": float (default: **0.75**) - waga wyniku ekstrapolacji w stosunku do ogólnego przemiszczenia (wiatr) przy obliczaniu położenia poszczeólnych punktów,
    - "vis_coeff": int (default: **1**) - współczynnik określający zagęszczenie punktów na animacji (1 - gęstość maksymalna),
    - "t_coeff": float (default: **0.25**) - współczynnik zanikania opadów (wartość 0 - oznacza, że intensywność opadu w czasie nie ulega spadkowi względem wartości wyekstrapolaowanej, wartość 1 - ozancza, że opad zanika po 100 minutach - krótkotrwały opad burzowy).