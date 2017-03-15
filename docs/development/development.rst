.. _development:

******************
Rozwój
******************

W tym dokumencie opisujemy opis procesu rozwoju aplkacji. Ma on postać FAQ, aby utrzymywać dokument prostym.


Jak zgłosić usterkę?
--------------------

Po prostu przejdź na https://github.com/watchdogpolska/feder/issues i utworz zgłoszenie.


Jak diagnozować funkcjonowanie poczty elektronicznej?
-----------------------------------------------------

W środowisku deweloperskim wiadomości e-mail są domyślnie wypisywane na konsole w oknie serwera WWW. Jeżeli chcesz zweryfikować np. formatowanie wiadomości zaleca się wykorzystanie `maildump`_, który możliwy jest do zainstalowania i uruchomienia poprzez::

    $ pip install maildump
    $ maildump

Następnie należy  ponownie uruchomić serwer WWW w następujący sposób ``EMAIL_URL=smtp://localhost:1025/ python manage.py runserver``. Wiadomości będą dostępne przez interfejs WWW 
pod adresem ``http://localhost:1080``. 

.. _`maildump`: https://github.com/ThiefMaster/maildump

Jak uruchomić automatyczne testy?
---------------------------------

Do prawidłowego uruchomienia automatycznych testów bezwzględnie wymagane jest zainstalowanie wszystkich deweloperskich pakietów. Można to osiągnąc poprzez::

    $ pip install -r requirements/dev.txt;

Następnie należy wywołać::

    $ python manage.py test

Warto wyróznić kilka przełączników, które mogą zapewnić sprawniejsze wykorzystanie testów:

- ``-v2`` oznacza, że będą na bieżąco wypisywane nazwy wszystkich testów wraz z ich rezultatem,
- ``--keepdb`` oznacza, że struktura bazy danych nie zostanie skasowana po wykonaniu testów, co pozwala oszczędzić jej tworzenie każdorazowo, co jednak uniemożliwi wykrycie testów np. w migracjach,
- ``--parallel 4`` oznacza, że testy będa wykonywane równolegle, a wcześniej zostaną utworzone 4 identyczne struktury bazy danych.

.. warning:: Warto zaznaczyć, że zrównoleglenie testów nie oznacza, że będą one wykonywane szybciej niż proces utworzenia dodatkowych baz danych może się wydłużyć o więcej niż sam proces wykonywania testów.


Jak wygenerować dokumentacje?
-----------------------------

Do prawidłowego uruchomienia automatycznych testów bezwzględnie wymagane jest zainstalowanie wszystkich deweloperskich pakietów. Można to osiągnąc poprzez::

    $ pip install -r requirements/dev.txt;

Nastepnie należy przejść do katalogu ``docs`` i wywołać::

    $ make html

Warto zaznaczyć, że aktualna dokumentacja jest budowana automatycznie i publikowana na `Read the Docs`_.

.. _`Read the Docs`: http://watchdog-kj-kultura.readthedocs.io/
