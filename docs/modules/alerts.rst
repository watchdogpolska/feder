.. _alerts:

**************************
Powiadomienia
**************************

Założenia
#########

Moduł stanowi komponent powiadomień do operatora o konieczności podjęcia akcji w systemie. Takie powiadomienia mogą być kierowane w związku z rozbieżnością w odpowiedziach, ale także ze względu na konieczność ochrony prywatności, gdyby jakiś urząd dokonał nieuprawnionego ujawnienia danych prywatnych.


Dane testowe
############

Dla modułu nie możliwe jest w środowisku deweloperskim dynamicznie wygenerowanie generowanych danych testowych.

 .. todo::
    Opracować generowanie danych testowych.

Architektura
############

Model
-----

.. automodule:: feder.alerts.models
   :members:


Panel administracyjny
---------------------

.. automodule:: feder.alerts.admin
   :members:

Procesorzy kontekstu
--------------------

.. automodule:: feder.alerts.context_processors
   :members:

Widoki
--------------------

.. automodule:: feder.alerts.views
   :members:
