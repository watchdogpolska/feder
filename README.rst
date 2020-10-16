 .. image:: https://coveralls.io/repos/watchdogpolska/feder/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/watchdogpolska/feder?branch=master

 .. image:: https://github.com/watchdogpolska/feder/workflows/Python%20package/badge.svg
    :target: https://github.com/watchdogpolska/feder/actions?workflow=Python+package

 .. image:: https://img.shields.io/github/license/watchdogpolska/feder.svg

 .. image:: https://david-dm.org/watchdogpolska/feder/dev-status.svg
     :target: https://david-dm.org/watchdogpolska/feder#info=devDependencies
     :alt: devDependency Status

Feder
=====

Mechanizm do automatycznego wysyłania wniosków o informację do dużej liczby podmiotów, automatycznego przyjmowania odpowiedzi, udostępnienia otrzymanych odpowiedzi do analizy pod wybranym kątem przez masowo angażowanych do tego zadania obywateli oraz  upubliczniania zweryfikowanych odpowiedzi i zestawień uzyskanych danych.

Testowanie w lokalnym środowisku
--------------------------------

Zbudowanie usługi:

.. code-block:: bash

    make build  # zbudowanie wszystkich zależności; może zająć trochę czasu przy pierwszym wywołaniu
    make wait_web  # inicjalizacja lokalnych zależności
    docker-compose up  # inicjalizacja samej aplikacji; po wykonaniu, aplikacja powinna być widoczna w localhost:8000

Inicjalizacja bazy danych:

.. code-block:: bash

    make importterc  # wypełnienie bazy jednostek organizacyjnych
    make createsuperuser  # stworzenie konta administratora
    make create_fake_socialapp  # utworzenie sztucznej integracji z platformą FB. Konieczne dla odblokowania ekranu logowania.

Inicjalizacja jest konieczna przed pierwszym użyciem. W trakcie wywoływania komend aplikacja powinna działać w tle, tj. wcześniej
należy wywołać komendę

.. code-block:: bash

    docker-compose up

Statyczna kontrola kodu
-----------------------

Statyczna kontrola kodu w projekcie służy do sprawdzenia, czy kod spełnia określone standardy jakości.

Wszystkie sprawdzenia kodu statycznego można uruchamiać za pomocą `pre-commit run`_. Są one
także weryfikowane w środowisku `GitHub Actions`_, przy każdej
propozycji zmian zawartości repozytorium.

.. _pre-commit run: https://pre-commit.com/
.. _GitHub Actions: https://github.com/watchdogpolska/feder/actions

W celu instalacji narzędzia do statycznej kontroli kodu, należy wykonać:

.. code-block:: bash

    pip install -r requirements/dev.txt

W celu wykonania kontroli statycznej kodu, należy wykonać:

.. code-block:: bash

    git add .
    make lint

Aby włączyć automatyczne sprawdzanie kodu przed stworzeniem zmiany (*commit*), należy wykonać:

.. code-block:: bash

    pre-commit install
