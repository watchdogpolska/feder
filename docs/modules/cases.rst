.. _cases:

**************************
Sprawy
**************************

Założenia
#########

Moduł odpowiedzialny jest za mechanizm "wątków" odnoszących się do konkretnego zapytania skierowanego do konkretnego urzędu. Każda sprawa jest związana tylko z jednym monitoringiem i jednym zapytaniem. W obrębie sprawy mogą być agregowane informacje różnej kategorii.

Dane testowe
############

Dla modułu nie możliwe jest w środowisku deweloperskim dynamicznie wygenerowanie generowanych danych testowych.

 .. todo::
    Opracować generowanie danych testowych.

Architektura
############

Model
-----

.. automodule:: feder.cases.models
   :members:


Panel administracyjny
---------------------

.. automodule:: feder.cases.admin
   :members:

Procesorzy kontekstu
--------------------

.. automodule:: feder.cases.context_processors
   :members:

Widoki
--------------------

.. automodule:: feder.cases.views
   :members:
