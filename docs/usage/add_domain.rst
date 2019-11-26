Aktywowanie obsługi domeny
==========================

Niniejszy opis ma na celu przedstawienie w jaki sposób - bazując
na stanie infrastruktury z dnia 26.11.2019 - należy aktywować
obsługę nowej domeny do systemu Fedrowania.

Do poprawnego doręczenia wiadomości do Fedrowania konieczne jest:

* dodanie domeny do systemu Fedrowania,
* skonfigurowanie serwera pocztowego do obsługiwania domeny Fedrowania
* działanie procesu do importowania wiadomości z serwera pocztowego
  do systemu Fedrowania.
* skonfigurowanie serwera nazw do obsługiwania domeny

Dodanie domeny
--------------

Aby dodać nową domenę do systemu Fedrowania należy:

* zalogować się do systemu Fedrowania
* skorzystać z Panelu administracyjnego dostępnego pod adresem `/admin/`
* przejść do zakładki *Domeny*
* dodać i oznaczyć jako aktywną nową domenę

Konfiguracja serwera pocztowego
-------------------------------

Na dzień 26 listopada 2019 roku obsługę serwera pocztowego dla potrzeb
Fedrowania zapewnia Zenbox. Realizowane jest to poprzez gromadzenie
wiadomości w jednej skrzynce pocztowej.

Aby skonfigurować serwer pocztowego do obsługiwania domeny Fedrowania należy:
* zalogować się do Panelu Zarządzania Zenbox,
* dodać domenę do konta Zenbox,
* skonfigurować przekierowanie catch-all na adres
`main@....`, zgodnie z domeną `siecobywatelska.pl`

Proces importowania wiadomości
------------------------------

Na dzień 26 listopada 2019 roku wykorzystywany jest współdzielony
proces importowania wiadomości dla wszystkich domen Fedrowania, gdyż
wykorzystywana jest - w poprzedniej sekcji - współdzielona skrzynka
pocztowa.

Aby skonfigurować proces importowania należy zmodyfikować parametrykontenera_
i zastosować odpowiednią rolę Ansible ponownie.

Aby zmodyfikować proces importowania należy zmodyfikować kod_zrodlowy_
importera. Kod źródłowy z gałęzi branch jest automatycznie wdrażany.

.. _parametrykontenera: https://github.com/watchdogpolska/infra/blob/0a945be625d019242ab3fdeac96684484aa57372/ansible/inventory/host_vars/helper.watchdog.internal/docker.yml#L68-L74
.. _kod_zrodlowy: https://github.com/watchdogpolska/imap-to-webhook

Konfiguracja serwera nazw
-------------------------

Na dzień 26 listopada 2019 roku wiadomości są odbierane z wykorzystaniem
serwera pocztowego zapewnionego przez Zenbox. Należy zapewnić poprawne
skonfigurowanie rekordów MX w strefie DNS domeny, aby wiadomość docierała
do serwera pocztowego Zenbox.
Na dzień 26 listopada 2019 roku wiadomości są wysyłane z wykorzystaniem
E-maillabs. Należy zapewnić poprawne skonfigurowanie DKIM, DMARC i SPF,
aby wiadomości zostały uznane za wiarygodne.

Aby zarządzać rekordami DNS w strefach DNS Stowarzyszenia należy zmodyfikować
 repozytorium infra_terraform_ zgodnie z regułami repozytorium.

.. _infra_terraform: https://github.com/watchdogpolska/infra-terraform
