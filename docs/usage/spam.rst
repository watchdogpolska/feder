*************
Obsługa spamu
*************

W okresie funkcjonowania systemu mogą wystąpić niepożądąne sytuacje związane z dostarczaniem przez systemy informatyczne
urzędu, albo – ze względu na publikacje adresów e-mail – inne podmioty niezamawianych informacji 
takich jak informacje handlowe, kartki świąteczne, których wartość informacyjna w konkretnej sprawie jest znikoma.

W celu obsługi tego rodzaju korespondencji został wprowadzony mechanizm zgłaszania spamu i oznaczania wiadomości jako 
spam.

Uprawnienia
-----------

System - w celu efektywnego rozłożenia zadań – wyposażony jest w mechanizm uprawnień. Osoba, która utworzyła monitoring
ma możliwość zarządzania nim i dysponuje wszelkimi uprawnieniami do tego. Może nadawać i odbierać uprawnienia
użytkownikom w danym monitoringu, a także nadawać im uprawnienia do takiego samego zarządzania.

Istnieją następujące uprawnienia związane z obsługą spamu:

Może widzieć dzienniki – ``can_view_log``
    uprawnia do zapoznania się z dziennikiem zgłoszeń w monitoringu

Może oznaczyć spam – ``can_mark_spam``
    uprawnia wpływające na zmianę działanie przycisku "Zgłoś spam" poprzez natychmiastowe ukrycie wiadomości

Proces obsługi
--------------

Na ekranie dowolnej wiadomości dostępny jest przycisk "Zgłoś spam". Po jego wybraniu przez użytkownika niezalogowanego
wiadomości trafiają do dziennika zgłoszeń.

Użytkownik, który posiada uprawnienie ``can_view_log`` otrzymuje powiadomienie o nowym wpisie w dzienniku
zgłoszeń.

Użytkownik zalogowany, który posiada uprawnienie ``can_mark_spam`` po wybraniu przycisku "Zgłoś spam" może ukryć
wiadomość oznaczoną jako spam. Ewentualnie wiadomość zostanie oznaczona jako prawidłowa, a wówczas nie będzie możliwe
ponowne zgłoszenie wiadomości jako spam. W obu przypadkach wpisy w dzienniku dotyczące danej wiadomości zostaną oznaczone
jako załatwione.

Wiadomość oznaczona jako spam – ze względów dowodowych i potencjalnego przyszłego wykorzystania np. uczenie maszynowego
automatycznego oznaczania podejrzanych wiadomości – nie jest całkowicie z systemu usunięta. Jest ona wyłącznie
wycofywana z publikacji. Z tego też względu nie należy wprowadzać niezgodne z stanem faktycznym oznaczenia wiadomości
jako spam, gdyż może to w przyszłości zakłócić maszynowe wnioskowanie.

