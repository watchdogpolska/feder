**************************
Zarządzanie korespondencja
**************************

Każda sprawa w systemie ma nadany unikalny adres e-mail. Pozwala on na automatyczną rejestracje przychodzącej wiadomości do konkretnej sprawy. Każda przychodząca wiadomość może odnosić się wyłącznie do jednej sprawy.

System odpowiedzialny jest za podstawowe operacje związane z zarządzanie korespondencją. W przypadku wysyłki jakiejkolwiek wiadomości z systemu w danej sprawie jest wykorzystywany unikalny adres e-mail.

Pole daty wiadomości identyfikuje czas rejestracji odpowiedzi przez system Stowarzyszenia. Nie jest to równoważne z czasem doręczenia do Stowarzyszenia, a także z czasem wysłania wiadomości przez instytucje ze względu na sposób działania poczty, która pozwala na dużą manipulacje tymi danymi. W przypadku chęci poznania czasu odpowiedzi przez urząd masz możliwość pobrania kopii wiadomości e-mail i otwarcia jej w programie pocztowym np. Thunderbird.

Uprawnienia
-----------

System Obywatelskiego Fedrowania Danych umożliwia zarówno wysyłkę korespondencji, sporządzenia na nią odpowiedzi, a także podstawowe mechanizmy recenzji projektów wiadomości poprzez pozostawienie wiadomości do przejrzenia przez osobę uprawnioną do wysyłki wiadomości.

Osoba, która utworzyła monitoring ma możliwość zarządzania nim i dysponuje wszelkimi uprawnieniami do tego. Może nadawać i odbierać uprawnienia użytkowniokom w danym monitoringu, a także nadawać im uprawnienia do takiego samego zarządzania.

Istnieją następujące uprawnienia związane z obiegiem korespondencji:

Może odpowiadać
    uprawnia do bezpośredniej wysyłki wiadomości do urzędu, a także do zatwierdzenia istniejących projektów wiadomości

Może dodawać szkic odpowiedzi
    uprawnia do tworzenia w danym monitoringu w ramach spraw szkiców odpowiedzi, które nie są wysyłane do urzędu, ale mogą zostać zatwierdzone przez osobę o stosownych uprawnieniach

Może usuwać list
    uprawnia do usuwania dowolnych wiadomości zarejestrowanych w systemie, które może być także wykorzystane do odrzucania szkiców wiadomości

Może edytować list
    uprawnienia do edycji dowolnej wiadomości zarejestrowanej w systemie, także zarejestrowanej i pochodzącej od urzędu.


Sporządzanie odpowiedzi
-----------------------

Aby udzielić odpowiedzi na list zarejestrowany w systemie przejdź na stronę sprawy, gdzie został on opublikowany. Następnie kliknij w jego tytuł, aby przejdź na stronę danego listu. U góry dostępny jest przycisk "Odpowiedź", który pozwala sporządzić tekstową odpowiedź do urzędu. Formularz (stosownie do uprawnień) może posiadać następujące przyciski zatwierdzania:

* Zapisz szkic - pozostawia daną wiadomość do przejrzenia przez użytkownika i nie wysyła jej do urzędu, jednak publikuje ją na stronie
* Wyślij odpowiedź - wysyła wiadomość do urzędu, który jest właściwy w danej sprawie.

.. hint::
   Jeżeli opcja "Odpowiedź" jest niedostępna - skontaktuj się z operatorem monitoringu, aby uzyskać stosowne uprawnienia.

Dziennik wiadomości
-------------------

W przypadku wychodzących wiadomości poczty elektronicznej rejestrowane są dane na temat transmisji wiadomości pochodzące z interfejsu programistycznego dostawcy usług Emaillabs.pl. Dane te są przez system automatycznie aktualizowane raz dziennie, co pozwala uzyskać informacje o stanie wiadomości wysłanych w Fedrowaniu.

Dzienniki możliwe są do przejrzenia z poziomu monitoringu i z poziomu sprawy. Aby się z nimi zapoznać przejdź do zakładki "Zobacz dzienniki" na odpowiedniej podstronie. Uzyskasz zestawienie wiadomości, które zawiera takie kolumny jak:

* ID - identyfikator wiadomości nadany przez E-maillabs,
* Sprawa - odwołanie do sprawy w jakiej dana wiadomość została wysłana,
* Status - ostatni poglądowy zarejestrowany status wiadomości,
* List - odwołanie do listu, który jest związany z daną wiadomością (jeżeli wykryto),
* Liczba wpisów - licznik wskazujący ile zmian dziennika odnotowano dla danej wiadomości.

.. hint::
   Jeżeli opcja "Zobacz dzienniki" jest niedostępna - skontaktuj się z operatorem monitoringu, aby uzyskać stosowne uprawnienia.

Po wybraniu identyfikatora wiadomości prezentowany są surowe dane odnoszące się do przebiegu doręczenia danej wiadomości stanowiące odpowiedź API. Te dane mogą kilkakrotnie ulegać zmianie, gdyż operator pocztowy w przypadku chwilowych trudności może ponowić wysyłkę w późniejszym terminie.

.. hint::
   Jeżeli zamierzasz wykorzystać dane dziennika wiadomości do celów dowodowych np. w sądzie zwróć się do administratora systemu o sporządzenie indywidualnej opinii na temat przebiegu doręczenia konkretnej wiadomości.

