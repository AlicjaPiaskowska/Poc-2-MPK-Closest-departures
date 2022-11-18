# Poc-2-MPK-Closest-departures

## Z czego składa się projekt?
**Są przygotowane dwa pliki python:**
- PoC_2_functions.py – plik z rozpisanymi wszystkimi funkcjami + flask
- PoC_2_Main.py – plik z wywołaniem funkcji

**Przygotowany jest plik HTML:**
- index.htmla

**Plik z bibliotekami:** 
- requirements.txt


## Działanie aplikacji:
**w formularzu są do wypełnienia pola:**
- Enter age: - należy wpisać wiek jako - pole jest liczbowe z zakresem od 0 do 150
- Enter time: - należy wpisać czas odjazdu. Należy wpisać godzinę i minuty. Godziny są ogarniczone od 0 do 23. Minuty od 0 do 59. Jeżeli użytkownik nie poda godziny, wówczas wzięta do aplikacji zostanie aktualna godzina
- Enter start/end point: - nalezy wpisać współrzędne punktów poczatkowych i końcowych - współrzędne są ogarniczone do przybliżonych współrzędnych położenia Polski

**Po wpisaniu danych pokazuje się tabela z 5 najbliższymi przystankami z naszej początkowej lokalizacji.**
- Tabela zawiera nazwę przystanku początkowego, najbliższą godzinę odjazdu, dystans to przystanku, nazwę najbliższego przystanku od punktu końcowego, czas przyjazdu na przystanek końcowy i odkległości naszego punktu końcowego od przystanku końcowego
 
## Problemy w aplikacji:

-	aplikacja działa dość powoli. Dla zoptymalizowania czasu działania w kodzie jest ogarniczenie na odległosci od przystanków – po podaniu punktu końcowego wyszukiwane są przystanki w odległości do 3 km od tego punktu. Czyli jak ktoś wybierze punkt, z którego do najbliższwego przystanku jest np. 4 km to aplikacja się zepsuje
**TO DO:** spróbować zoptymalizować zapytania, żeby szybciej generował się wynik końcowy. 
-	Jeżeli użytkownik poda źle współrzędne to może dostać zupełnie inny wynik niż oczekiwał
**TO DO:** potrzeba byłaby weryfikacja współrzędnych czyli np.:
      - Czy na pewno są wpisane w odpowiednim formacie, 
- po wybraniu danych i kliknięciu "submit" pokazuje się tabelka, ale znikają wszystkie dane wpisane przez użytkownika - można np. jakoś zachować wybrane dane
- jeżeli nie ma przystanku dla okreslonych kryteriów, wówczas pokazuje się pusta tabelka - można dodać informacje, że przy wybranych kryteriach nie znaleziono połączenia


## Dodatkowo do zrobienia + potencjalne problemy:
-	Testy
-	Na ten moment pliki txt ze strony internetowej przerabiane są na csv w taki sposób, że zmieniane jest rozszerzenie plików z .txt na .csv – teraz to działa ok, ale nie wiem czy to najlepszy sposób, więc warto się zastanawić nad tym


## jakie testy można zrobić?
-	czy jak wpiszemy godzinę 2 i 2 minut to czy wyświetli się 2:02 czy 2:20
-	czy jak wpiszemy wiek np. 24.5 to nam zaokrągli do 24 czy 25 - może się to okazać kluczowe na graniczach wieku
-	czy prawidłowo liczy się odległość (podac konkretne wpsółrzędne i odbieść się do odległości np. z google)
-	czy pokazuje nam przystanek w dobrym kierunku
-	czy wybierają się dobre odległości do punktów w zależności od wieku 
