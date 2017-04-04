.. _teryt:

*********************************
Jednostki podziału terytorialnego
*********************************

Założenia
#########

Moduł dostarcza informacje na temat podziału terytorialnego w Polsce. Zapewnia przegląd instytucji w danym regionie. Oparty jest o moduł `django-teryt-tree`_ dla którego istnieje odrębna dokumentacja.

.. _django-teryt-tree: https://github.com/ad-m/django-teryt-tree

Dane testowe
############

Dla modułu możliwe jest zaimportowanie automatyczne danych testowych. Mogą posłużyć do tego polecenia::

    wget "http://www.stat.gov.pl/broker/access/prefile/downloadPreFile.jspa?id=1110" -O TERC.xml.zip;
    unzip TERC.xml.zip;
    pip install lxml;
    python manage.py load_teryt TERC.xml;
    rm TERC.xml*;

W razie trudności - patrz sekcja `"Quickstart" dokumentacji django-teryt-tree <https://github.com/ad-m/django-teryt-tree#quickstart>`_ .

Architektura
############

Model
-----

.. automodule:: feder.teryt.models
   :members:


Panel administracyjny
---------------------

.. automodule:: feder.teryt.admin
   :members:

Procesorzy kontekstu
--------------------

.. automodule:: feder.teryt.context_processors
   :members:

Widoki
--------------------

.. automodule:: feder.teryt.views
   :members:
