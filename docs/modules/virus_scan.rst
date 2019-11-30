.. _virus_scan:

*********************************
Skanowanie antywirusowe
*********************************

Założenia
#########

Moduł odpowiedzialny jest za skanowanie wybranych przez użytkowników
plików z użyciem skanerów antywirusowych on-line.

Dostępne są następujące silniki skanowania:

* VirusTotal - limit 4 żądań / minutę, brak limitu plików, szczegóły
* MetaDefender Cloud - limit 10 żądań / minutę, 100 żądań / dzień, szczegóły: https://metadefender.opswat.com/licensing
* AttachmentScanner - brak limitów, niska skuteczność, szczegóły: https://www.attachmentscanner.com/pricing

Architektura
############

Model
-----

.. automodule:: feder.virus_scan.models
   :members:


Widoki
--------------------

.. automodule:: feder.virus_scan.views
   :members:

Panel administracyjny
---------------------

.. automodule:: feder.virus_scan.admin
   :members:

Silniki
---------------------

.. automodule:: feder.virus_scan.engine
   :members:
