.. _institutions:

**************************
Instytucje
**************************

Założenia
#########

Moduł stanowi mechanizm gromadzenia danych adresowych o instytucjach i przedstawienie spraw w jakich dany urząd jest zaaganżowany.

Dane testowe
############

Generowanie testowych danych możliwe jest przykładowo z wykorzystaniem::

    python manage.py loadtestdata institutions.Institution:25

Architektura
############

Model
-----

.. automodule:: feder.institutions.models
   :members:


Panel administracyjny
---------------------

.. automodule:: feder.institutions.admin
   :members:

Procesorzy kontekstu
--------------------

.. automodule:: feder.institutions.context_processors
   :members:

Widoki
--------------------

.. automodule:: feder.institutions.views
   :members:
