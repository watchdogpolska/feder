.. _letters_logs:

***************
Dziennik listów
***************

Założenia
#########

Moduł przeznaczony jest do gromadzenia informacji na temat dostarczenia wiadomości przesłanych w monitoringu / sprawie, a docelowo także indywidualnych wiadomości.

Moduł dostarcza polecenie ``python manage.py update_emaillabs``, który pobiera aktualne wpisy dziennika z `Emaillabs <https://emaillabs.pl/>`_ , a następnie archiwizuje te, które dotyczą spraw zarejestrowanych w systemie.

Dostęp do dzienników jest możliwy przez użytkownika, który ma uprawnienie ``view_logs`` w danym monitoringu.

Dane testowe
############

Dla modułu istnieją stosowne fabryki w module ``feder.letters.logs.factories``.


Architektura
############

Model
-----

.. automodule:: feder.letters.logs.models
   :members:


Panel administracyjny
---------------------

.. automodule:: feder.letters.logs.admin
    :members:

Widoki
--------------------

.. automodule:: feder.letters.logs.views
   :members:
