.. _fixtures:

************
Dane testowe
************

W celu szybkiego rozruchu aplikacji możliwe jest wygenerowanie lub wczytanie pewnych danych początkowych. Szczegółowe instrukcje zostały przedstawione w modułach właściwych modułów. 

Zaleca się jednak następującą sekwencje::

1. :ref:`teryt`
2. :ref:`monitorings`
3. :ref:`institutions`
4. :ref:`cases`

Wykorzystywane w aplikacj są jednak także moduły, które nie wspierają automatycznego generowania swojej treści ze względu na wykorzystywanie złożonej strukturys danych. Ich wypełnienie danymi jest możliwe z poziomu interfejsu użytkownika. Każdy moduł jednak zawiera submoduł ``fixtures``, który może stanowić źródło wiedzy o pożądanej strukturze.

