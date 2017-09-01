.. _letters:

*****
Listy
*****

Założenia
#########

Moduł odpowiedzialny za indywidualny komunikat wymieniony pomiedzy systemem, a urzędem. Zapewnia odbiór korespondencji w formie e-mailowej wraz z załącznikami i jej publikacji.

Odbiór korespondencji w formie e-mailowej realizowany jest z wsparciem aplikacji `django-mailbox <https://github.com/coddingtonbear/django-mailbox>`_ .

Dane testowe
############

Dla modułu nie możliwe jest w środowisku deweloperskim dynamicznie wygenerowanie generowanych danych testowych.

 .. todo::
    Opracować generowanie danych testowych.

Architektura
############

Model
-----

.. automodule:: feder.letters.models
   :members:


Panel administracyjny
---------------------

.. automodule:: feder.letters.admin
   :members:

Widoki
--------------------

.. automodule:: feder.letters.views
   :members:

