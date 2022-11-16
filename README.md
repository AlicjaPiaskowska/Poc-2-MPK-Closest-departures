# Poc-2-MPK-Closest-departures

## Z czego składa się projekt?
**Są przygotowane dwa pliki python:**
- PoC_2_functions.py – plik z rozpisanymi wszystkimi funkcjami + flask
- PoC_2_Main.py – plik z wywołaniem funkcji

**Przygotowany jest plik HTML:**
- index.html

**Plik z bibliotekami:** 
- requirements.txt


## Działanie aplikacji:
**w formularzu są do wypełnienia pola:**
- Enter age: - należy wpisać wiek jako integer
- Enter time: - należy wpisać czas odjazdu w formacie HH:MM:SS
- Enter start/end point: - nalezy wpisać współrzędne punktów poczatkowych i końcowych

**Po wpisaniu danych pokazuje się tabela z 5 najbliższymi przystankami z naszej początkowej lokalizacji.**
- Tabela zawiera nazwę przystanku początkowego, najbliższą godzinę odjazdu, dystans to przystanku, nazwę najbliższego przystanku od punktu końcowego, czas przyjazdu na przystanek końcowy i odkległości naszego punktu końcowego od przystanku końcowego
 
## Problemy w aplikacji:
- jeżeli wpiszemy wiek jako np. String wówczas popsuje nam się aplikacja
**TO DO:**  np. Po wpisaniu stringa czy innego typu danych podać informację, że nie jest to liczba i należy wpisać liczbę poprawnie 
-	czas jest podany jako string i nalezy wpisać go z dwukropkiem i z sekundami
**TO DO:** zmienić tę funkcjonalność tak, żeby nie trzeba było używać dwukropków i nie trzeba było wpisywać sekund. Aktualnie jest to pole obowiązkowe, więc należy zmienić je tak, żeby było opcjonalne i jeżeli się nie poda godziny to żeby brało aktualną godzinę
-	aplikacja działa dość powoli. Dla zoptymalizowania czasu działania w kodzie jest ogarniczenie na odległosci od przystanków – po podaniu punktu końcowego wyszukiwane są przystanki w odległości do 3 km od tego punktu. Czyli jak ktoś wybierze punkt, z którego do najbliższwego przystanku jest np. 4 km to aplikacja się zepsuje
**TO DO:** spróbować zoptymalizować zapytania, żeby szybciej generował się wynik końcowy. 
-	Jeżeli użytkownik poda źle współrzędne to może dostać zupełnie inny wynik niż oczekiwał
**TO DO:** potrzeba byłaby weryfikacja współrzędnych czyli np.:
      - Czy na pewno są wpisane w odpowiednim formacie, 
      - Czy znajdują się w jakiś określonych granicach – np. W granicach Wrocławia/Polski – bo jeżeli zamiast x wpiszemy y to możemy pewnie wylądować gdzieś w Afryce
- po wybraniu danych i kliknięciu "submit" pokazuje się tabelka, ale znikają wszystkie dane wpisane przez użytkownika - można np. jakoś zachować wybrane dane
- jeżeli nie ma przystanku dla okreslonych kryteriów, wówczas pokazuje się pusta tabelka - można dodać informacje, że przy wybranych kryteriach nie znaleziono połączenia

## Problemy z kodem:
mam dwa pliki python. W jednym (o nazwie PoC_2_functions) są wszystkie funkcje, w drugim (PoC_2_Main) są wywołania tych funkcji. W pierwszym pliku mam też funkcje używające flask, po wywołaniu kodu z tego pierwszego pliku w konsoli pojawia się adres HTTP, i jak go klikniemy to pojawia się formularz do wypełnienia przez użytkownika. Nie wiem jeszcze co zrobić, żeby adres HTTP pojawiał się przy wowołaniu kodu z pliku „PoC_2_Main”


## Dodatkowo do zrobienia + potencjalne problemy:
-	Testy
-	Na ten moment pliki txt ze strony internetowej przerabiane są na csv w taki sposób, że zmieniane jest rozszerzenie plików z .txt na .csv – teraz to działa ok, ale nie wiem czy to najlepszy sposób, więc warto się zastanawić nad tym
-	Usystematyzowanie nazwy funkcji, zmiennych, komentarzy i wyświetlanych w konsoli komunikatów tak, żeby były w jednym języku i były oczywiste
-	Nie wszystkie biblioteki w pliku „requirements.txt” są niezbędne (często jakieś biblioteki były instalowane do przetestowania jakieś funkcjonalności i zostały) – zrobić z tym porządek
