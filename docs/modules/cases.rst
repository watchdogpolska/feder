.. _cases:

**************************
Sprawy
**************************

Założenia
#########

Moduł odpowiedzialny jest za mechanizm "wątków" odnoszących się do konkretnego zapytania skierowanego do konkretnego urzędu. Każda sprawa jest związana tylko z jednym monitoringiem i jednym zapytaniem. W obrębie sprawy mogą być agregowane informacje różnej kategorii.

Dane testowe
############

Wygenerowanie testowych danych dla modułu jest możliwe przykładowo z wykorzystaniem::

    python manage.py loadtestdata cases.Case:25

Architektura
############

Model
-----

.. automodule:: feder.cases.models
   :members:

Widoki
--------------------

.. automodule:: feder.cases.views
   :members:
