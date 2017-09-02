.. _questionaries:

**************************
Kwestionariusze
**************************

Założenia
#########

Moduł stanowi mechanizm analizy danych do postaci zagregowanej.

Encja "kwestionariusz" (``Questionary``) zapewnia definicje na poziomie monitoringu na jakie pytania użytkownik ma odpowiedzieć w ramach opracowania danych w konkretnej sprawie.

Encja "pytanie" (``Question``) zapewnia definicje konkretnego pytania - części składowego pytania, a także określa kolejności pytań występujących w kwestionariuszu. Każde pytanie może mieć różny format (pytanie tekstowe, pytanie wielokrotnego wyboru itp.), dzięki mechanizmowi `modulator`.


Dane testowe
############

Dla modułu nie możliwe jest w środowisku deweloperskim dynamicznie wygenerowanie generowanych danych testowych.

 .. todo::
    Opracować generowanie danych testowych.

Architektura
############

Model
-----

.. automodule:: feder.questionaries.models
   :members:


Widoki
--------------------

.. automodule:: feder.questionaries.views
   :members:
