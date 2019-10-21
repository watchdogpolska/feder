.. _development:

Rozwój
======

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

Do prawidłowego uruchomienia automatycznych testów bezwzględnie wymagane jest zainstalowanie wszystkich deweloperskich pakietów. Można to osiągnąć poprzez::

    $ make build

Następnie należy wywołać::

    $ make test


Jak wygenerować dokumentacje?
-----------------------------

Do prawidłowego zbudowania dokumentacji bezwzględnie wymagane jest zainstalowanie wszystkich deweloperskich pakietów. Można to osiągnąć poprzez::

    $ make build

Następnie wywołać::

    $ make docs

Warto zaznaczyć, że aktualna dokumentacja jest budowana automatycznie i publikowana na `Read the Docs`_.

.. _`Read the Docs`: http://watchdog-kj-kultura.readthedocs.io/


.. _question_test_data:

Jak pozyskać testowe dane?
--------------------------

W celu utworzenia danych testowych należy zaimportować podział terytorialny zgodnie z instrukcją biblioteki `django-teryt-tree <https://github.com/ad-m/django-teryt-tree#quickstart>`_. Następnie można wykorzystać poniższy kod::

    from feder.letters.factories import SendOutgoingLetterFactory
    SendOutgoingLetterFactory()

Jeżeli otrzymujesz::

    IntegrityError: (1062, "Duplicate entry '1' for key 'PRIMARY'")

oznacza to w bazie danych istnieją rekordy, które kolidują z istniejącymi danymi. Możesz ponownie uruchomić ``SendOutgoingLetterFactory()``, a licznik powinien wzrosnąć, co pozwoli uniknąć kolizji, albo usuń zgromadzone dane.

Ręcznie taka procedura polega na dodaniu instytucji, potem stworzeniu monitoringu i przypisaniu do niego instytucje. Wówczas powinny istnieć także list w sprawie.

Jakie jest hasło dla automatycznie utworzonego użytkownika?
-----------------------------------------------------------

Domyślnym hasłem utworzonych :ref:`question_test_data` to ``pass``. Zostało ono określone w klasie ``feder.users.UserFactory``.

.. _add_admin_account:

Jak utworzyć konto administratora?
----------------------------------

Konto administratora może zostać utworzone poprzez polecenie ``python manage.py creatsuperuser``. Szczegółowe parametry są przedstawione na `odpowiedniej podstronie dokumentacji Django <https://docs.djangoproject.com/en/1.11/ref/django-admin/#createsuperuser>`_.


W jaki sposób postępować w przypadku błędu ``No Facebook app configured`` na ekranie logowania?
-------------------------------------------------------------------------------------------------

Przedstawiony błąd związany jest z próbą uzyskania kluczy API dla logowania społecznościowego za pośrednictwem Facebook-a. Należy utworzyć konto adinistratora (zob. :ref:`add_admin_account` ), następnie zalogować się do panelu administracyjnego (``http://localhost:8000/admin/``). Ostatecznie należy dodać aplikacje ``ScoialApp`` (``https://localhost:8000/admin/socialaccount/socialapp/``) typu Facebook z losowymi danymi kluczy.
