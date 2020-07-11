Uprawnienia
===========

System Obywatelskie Fedrowanie Danych był projektowany z założeniem wysokiej granulacji uprawnień w celu umożliwienia
możliwie skutecznego powierzenia uprawnień użytkownikom o różnym stopniu odpowiedzialności.

Istnieją następujące globalne atrybuty użytkownika:

W zespole
    Określa czy użytkownik może zalogować się do panelu admina.
Status superużytkownika
    Oznacza, że ten użytkownik ma wszystkie uprawnienia bez jawnego ich przypisywania.

Jak również następujące globalne uprawnienia:

Can add Monitoring - ``monitorings.add_monitoring``
    Oznacza, że ten użytkownik może samodzielnie utworzyć nowy monitoring

 - ``letters.recognize_letter``
    Określa, że użytkownik może ręcznie rozpoznać list, który nie został przypisany do sprawy

Monitoring
----------

Osoba, która utworzyła monitoring ma możliwość zarządzania nim i dysponuje niezbędnymi uprawnieniami do tego.
Może nadawać i odbierać uprawnienia użytkownikom w danym monitoringu, a także nadawać im uprawnienia do takiego samego
zarządzania.


'change_monitoring', 'delete_monitoring',
'add_case', 'change_case', 'delete_case', 
'reply', 'add_draft',
'view_alert', 'change_alert', 'delete_alert', 
'manage_perm', 

Poszczególne uprawnienia są szczegółowo opisane w ramach właściwych części podręcznika użytkownika.

 - ``monitorings.add_case`` (domyślne dla autora monitoringu)
    Określa, że użytkownik może dodawać nową sprawę
 - ``monitorings.add_draft`` (domyślne dla autora monitoringu)
    Określa, że użytkownik może dodać szkic listu (bez wysyłania)
 - ``monitorings.add_letter``
    Określa, że użytkownik może dodać nowy list (bez wysyłania)
 - ``monitorings.change_alert`` (domyślne dla autora monitoringu)
    Określa, że może edytować wpis w dzienniku
 - ``monitorings.change_case``
    Określa, że może dodać nową sprawę
 - ``monitorings.change_letter``
    Określa, że może edytować listy
 - ``monitorings.change_monitoring`` (domyślne dla autora monitoringu)
    Określa, że może edytowac monitoring (jego opis, szablon wniosku itp. )
 - ``monitorings.delete_alert`` (domyślne dla autora monitoringu)
    Określa, że może usuwać zadanie
 - ``monitorings.delete_case`` (domyślne dla autora monitoringu)
    Określa, że może usuwać sprawę
 - ``monitorings.delete_letter``
    Określa, że może usuwać listy
 - ``monitorings.delete_monitoring`` (domyślne dla autora monitoringu)
    Określa, że może usuwać monitoringi
 - ``monitorings.manage_perm`` (domyślne dla autora monitoringu)
    Określa, że zarządzać uprawnieniami w monitoringu
 - ``monitorings.reply`` (domyślne dla autora monitoringu)
    Określa, że wysyłać monitoring do wnioskodawcy
 - ``monitorings.view_alert`` (domyślne dla autora monitoringu)
    Określa, że wyświetlać jeden wpis w dzienniku
 - ``monitorings.view_log``
    Określa, że wyświetlać dziennik wysyłki korespondencji e-mailowej

Instytucje
----------

Osoba, która posiada właściwe uprawnienia może zarządzać katalogiem instytucji.

Powiązane z katalogiem uprawnienia to:

 - ``institutions.add_institution``
    Określa, że użytkownik może dodawać instytucje
 - ``institutions.change_institution``
    Określa, że użytkownik może usuwać instytucje
 - ``institutions.delete_institution``
    Określa, że użytkownik może edytować instytucje

