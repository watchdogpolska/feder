.. _monitorings:

**************************
Monitoringi
**************************

Założenia
#########

Moduł stanowi komponent, który agreguje sprawy związane z różnymi urzędami, które odnoszą się do zbiernia informacji tej samej kategorii. Zatem monitoringiem będzie np. zainteresowanie wysoką opłaty za śmieci w Polsce. Na tej postawie system tworzy liczne sprawy dla każdego urzędu, który ma być objęty badaniem.

Dane testowe
############

Wygenerowanie danych testowych może zostać przeprowadzone z wykorzystaniem polecenia::

    python manage.py loadtestdata monitorings.Monitoring:25

Architektura
############

Model
-----

.. automodule:: feder.monitorings.models
   :members:


Panel administracyjny
---------------------

.. automodule:: feder.monitorings.admin
   :members:

Procesorzy kontekstu
--------------------

.. automodule:: feder.monitorings.context_processors
   :members:

Widoki
--------------------

.. automodule:: feder.monitorings.views
   :members:
