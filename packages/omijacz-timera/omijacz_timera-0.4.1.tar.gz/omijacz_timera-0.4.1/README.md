<h1 align="center">🚘 Omijacz Timera Prawojazdy 🚔</h1>

[![Build Status](https://travis-ci.org/taniotanio7/omijacz-timera-prawojazdy.svg?branch=master)](https://travis-ci.org/taniotanio7/omijacz-timera-prawojazdy)
[![Maintainability](https://api.codeclimate.com/v1/badges/f1483bc09e7003232cb7/maintainability)](https://codeclimate.com/github/taniotanio7/omijacz-timera-prawojazdy/maintainability)
[![Updates](https://pyup.io/repos/github/taniotanio7/omijacz-timera-prawojazdy/shield.svg)](https://pyup.io/repos/github/taniotanio7/omijacz-timera-prawojazdy/)

> 🎉 Żyj! 🎉
>
> Nie trać czasu na nudne, powtarzające się slajdy...

## Opis

Skrypt pozwala na "ominięcie" slajdów w kursie e-learningowym na stronie **prawojazdy.com.pl**.

Niestety obecnie używana w serwisie metoda komunikacji z serwerem jest bardzo zawodna, zwłaszcza podczas korzystania
z urządzeń mobilnych.

Obejście fakt, że po stronie serwera nie następuje żadna weryfikacja czy w rzeczywistości minął odpowiedni czas
potrzebny na oznaczenie slajdu jako obejrzany.

### :poop: Znane bugi

- Problem z obsługą slajdów z pytaniem (skrypt po prostu czeka 10 sekund, a następnie przechodzi dalej)
- Po ponownym zalogowaniu się na stronie wyświetla się informacja o tym, że aktywna jest inna sesja. Wystarczy wejść na główną jeszcze raz i ponownie wybrać kurs.


## Instalacja

Musisz posiadać zainstalowanego Pythona, pip oraz **Google Chrome**.

W wierszu poleceń / terminalu wpisz:

```python
pip install omijacz-timera
```
lub
```python
pip3 install omijacz-timera
```
*Komenda zależy od twojej instalacji Pythona*

### Ręczna instalacja

1. [Pobierz .zip](https://github.com/taniotanio7/omijacz-timera-prawojazdy/archive/master.zip) z repozytorium i rozpakuj

2. W PATH Pythona zainstaluj [najnowszą wersję ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)

*Wystarczy że plik znajdzie się w jednym z wymienionych folderów*

> 💥 Uwaga! ChromeDriver musi być wypakowany z archiwum

> 🍻 Protip: PATH można sprawdzić wpisując...
>
> Windows: `PATH`
>
> Linux: `echo $PATH`

3. Przejdź do folderu z projektem:

```
cd omijacz-timera-prawojazdy
```

4. Zainstaluj z użyciem setup.py:
```
python setup.py install
```


## Korzystanie

1. W wierszu poleceń / terminalu wpisz:

```
omijacz_timera
```

Otworzy się nowy proces Google Chrome:

![Nowe okno Google Chrome ze stroną do logowania](/readme_images/login_screen.png)

2. Zaloguj się!

![Strona po wpisaniu danych do logwania](/readme_images/login_screen_filled.png)

> Twoje hasło nie jest nigdzie zapisywane zostaje użyte tylko do zalogowania się w przeglądarce

3. Kliknij w przycisk "Przejdź do kursu"

![Przycisk przejdź do kursu](/readme_images/course_select_main.png)

4. Wybierz lekcję

![Wybór lekcji](/readme_images/course_select_choice.png)

5. Ciesz się obejrzaną lekcją!

![Automatyzacja slajdów](/readme_images/course_automated.png)

### :rotating_light: Dobra rada :rotating_light:

> Mimo wszystko zalecałbym po "odhaczeniu" lekcji obejrzenie wszystkich slajdów.
>
> Dzięki temu coś zapamiętasz, a nie będziesz musiał dodatkowo marnować swojego czasu
> na odczekanie, aż będziesz mógł przejść dalej


## :poop: Zgłaszanie błędów

Problemy można zgłaszać tutaj: https://github.com/taniotanio7/omijacz-timera-prawojazdy/issues

## :construction_worker: Development environment

Te instrukcje pomogą Ci uruchomić kopię projektu na twoim lokalnym urządzeniu w celu programowania lub testowania. 

### Zanim zaczniesz

Co potrzebujesz, aby rozpocząć

- Python
- pip
- git

### Instalacja

Krok po kroku jak utworzyć środowisko programistyczne.

Utwórz kopię repozytorium git

```
git clone https://github.com/taniotanio7/omijacz-timera-prawojazdy.git
```

Zainstaluj potrzebne zależności

```
pip install -r requirements.txt
```

## :recycle: Todo

- [x] Przyśpieszyć działanie
- [x] Dodać pobieranie ChromeDriver podczas instalacji
- [ ] Poprawić opis na PyPI
- [ ] Refaktoryzacja
- [ ] Wylogowywanie się po zakończonej sesjii
- [ ] Poprawa obsługi slajdów z pytaniem
- [ ] Możliwość wyboru innych przeglądarek niż Chrome

## :sunglasses: Autorzy

* **Jonatan Witoszek** - *Początek* - [taniotanio7](https://github.com/taniotanio7)

Zobacz pełną listę [osób](https://github.com/taniotanio7/omijacz-timera-prawojazdy/contributors), która pomogła w projekcie.

## :page_facing_up: Licence

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## :clap: Acknowledgments

* Hat tip to Kenneth Reitz for his setup.py example!
