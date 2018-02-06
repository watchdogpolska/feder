*******************
Koncepcja aplikacji
*******************

Do najważniejszych problemów debaty publicznej niewątpliwie zalicza się częste opieranie argumentacji na nieweryfikowalnych lub nieaktualnych danych.

Informacje posiadane przez organy administracji publicznej są skarbnicą wiedzy. Ich skuteczne wykorzystanie pozwoliłoby rozwiać wiele pojawiających się wątpliwości. Niestety, forma ich przechowywania i udostępniania często uniemożliwia łatwe ich odczytanie oraz intepretację, w szczególności przy użyciu technik cyfrowych.

Obywatelskie fedrowanie danych jest projektem powstałym w odpowiedzi na to wyzwanie. Ma na celu usystematyzowanie dużej liczby informacji spływających od instytucji publicznych oraz zapisanie ich w formie łatwej do analizy, zarówno przez człowieka, jak i maszynę. To obywatele-wolontariusze, którym zależy na jakości życia publicznego w Polsce, czytają udzielone przez organy odpowiedzi i uzupełniają bazę danych poprzez wykorzystanie intuicyjnego mechanizmu ankiet. Zebrane i uporządkowane dane służą następnie do przeprowadzania badań, które to przyczyniają się do wzrostu świadomości społecznej i poprawy jakości rządzenia.

Cele społeczne
--------------

* Szybka i zbiorowa analiza danych nieistniejących w żadnych repozytoriach i nie istniejących w formie możliwej do odczytu maszynowego. Do wykorzystywania w kampaniach rzeczniczych lub jako dowody w systemie tworzenia prawa.
* Masowa edukacja obywatelska na temat tego, jakie informacje można uzyskać od władz i jak wyglądają ich odpowiedzi oraz korespondencja z nimi, a także jak sprawdzać wypowiedzi pojawiające się w debacie publicznej.

Cele dodatkowe
--------------

Aplikacja uniwersalna, do przystosowania dla różnych akcji przez różne organizacje.

Zasada działania
----------------

W pierwszej kolejności użycie aplikacji wymaga dostarczenia danych adresowych instytucji, co zapewnia moduł :ref:`institutions`. Po wypełnieniu bazy adresowej wymagane jest utworzenie monitoringu (zob. :ref:`monitorings`), co zapewnia jednocześnie utworzenie spraw (zob. :ref:`cases`), a także wysłanie stworzenie w nich pierwszych listów (zob. :ref:`letters`).

Wysyłka listów systemu odbywa się z wykorzystaniem poczty elektronicznej. Zazwyczaj jeden wzórw listu jest kierowany do kilkudziesięciu podmiotów. W odpowiedzi urząd ma obowiązek udzielenia nam odpowiedzi w formie i sposób określony w wniosku - na dedykowany adres e-mail. Wiadomośći są interpretowane i pobierane do systemu przez moduł :ref:`letters`, który zapewnia również przypisanie korespondencji do danej sprawy (zob. :ref:`cases`), która związana jest z konkretnym urzędem.

Po zarejestrowaniu odpowiedniej ilości odpowiedzi możliwe konieczne jest utworzenie w monitoringu stworzenia kwestionariusza (zob. :ref:`questionaries`), a następnie na jego podstawie w licznych sprawach utworzenie zadań (zob. :ref:`tasks`). Wówczas dane są przetwarznae przez użytkowników, co zostało przedstawione na diagramie:

.. figure:: https://s.jawne.info.pl/2w8pGDd
   :alt: Diagram sekwencji procesu analizy danych

.. code::

    Feder->Urząd: wniosek o informacje publiczną – e-mail
    Urząd->Feder: odpowiedź – e-mail
    Obywatel 1->Feder: zapytanie o stan sprawy – strona WWWW
    Feder->Obywatel 1: odpowiedź urzędu i ankieta
    Obywatel 2->Feder: zapytanie o stan sprawy – strona WWWW
    Feder->Obywatel 2: odpowiedź urzędu i ankieta
    Obywatel 2->Feder: wypełniona ankieta
    Feder->Feder: porównanie ankiet urzędu

    opt
        Feder->Operator: powiadomienie o rozbieżnościach
        Operator->Operator: ocena ankiet i odpowiedzi urzędu
        Operator->Feder: wybrana ankieta
    end

    Feder->Operator: arkusz kalkulacyjny z danymi


System wyposażony winien być w mechanizm weryfikacji rozbieżności w ankietach, gdyby dochodziło do rozbieżnych interpretacji udzielonych odpowiedzi. Wówczas operator dokonuje wyboru właściwej ankiety, albo zgłasza odpowiedzi własne.

Ankiety związane z danym kwestionariuszem mogą być wyeksportowane i analizowane z wykorzystaniem właściwych narzędzi.

Przykłady zastosowań
--------------------

Przepisywanie skróconych informacji i dostarczanie danych liczbowych
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

W 2012 Sieć Obywatelska Watchdog Polska włączyła się w kampanię przeciw zmianom w ustawie o zgromadzeniach. Zmiany wprowadzano pod wpływem zamieszek przy okazji Dnia Niepodległości w Warszawie. Miały one zwiększać kontrolę i de facto nakładać duże obowiązki na organizatorów zgromadzeń. Celem zbierania danych było uzyskanie informacji możliwych do pokazania parlamentarzystom, o tym że zmiany które chcą wprowadzić dotkną także organizatorów zgromadzeń w małych miejscowościach. Przekaz miał uświadomić, że zmian prawa nie można dokonywać bez widzenia całości obszaru, którego będą one dotyczyły oraz że zmiany mogą zamrozić i tak niewielką aktywność obywatelską.

Aby dowiedzieć się jak wglądają zgromadzenia w małych miejscowościach (duże często mają rejestr w formie możliwej do odczytu w BIPie), Sieć Obywatelska Watchdog Polska wysłała wniosek o informację do wybranych urzędów gmin o:.

* skany wszystkich wniosków zgłaszających zgromadzenie za lata 2010-2012
* skany ewentualnych decyzji odmawiających zgłaszanie zgromadzenia za lata 2010-2012

Z otrzymanych odpowiedzi można było uzyskać głównie dane jakościowe:
* jakie podmioty zgłaszają zgromadzenia (czy są to osoby indywidualne, związki zawodowe, kościoły, organizacje)
* w jakiej sprawie są te zgromadzenia organizowane oraz dane ilościowe
* ile rocznie zgłasza się zgromadzeń (zwłaszcza w mniejszych miejscowościach)

Dostarczanie danych liczbowych
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

W 2012 roku zwiększyła się nieco aktywność obywatelska w zakresie wnioskowania o informację. Był to wynik błędów rządu przy nowelizacji ustawy o dostępie do informacji publicznej i dużego nagłośnienia medialnego. Częściowo zapewne także wynik aktywności Sieci Obywatelskiej Watchdog Polska i innych organizacji. Nie bez znaczenia jest, że firmy zbierające dane, nauczyły się korzystać z prawa do informacji, co szczególnie oburza urzędników. Lobbing urzędników był i jest na tyle skuteczny, że coraz więcej szanowanych osób zabierających głos w debacie publicznej powtarza sformułowanie o „nadużywaniu prawa do informacji” Ponieważ może to skutkować realnymi zmianami w prawie, Sieć Obywatelska Watchdog Polska wysłała do wszystkich urzędów gmin (2500) wniosek, który miał zweryfikować jaki jest faktyczny stan wnioskowania i zbadać jakie dane są w ogóle dostępne. Wyniki pokazały, że realny poziom wnioskowania jest bardzo niski – od kilku do kilkudziesięciu wniosków rocznie (poza największymi miastami i ekstremalnymi sytuacjami), a wzrost pomiędzy 2011 i 2012 roku jest znikomy.

Aby uzyskać te informacje, Sieć Obywatelka Watchdog Polska zadała następujące pytania:

1.  Ile wniosków o informację publiczną otrzymał urząd w 2011 roku
2.  Ile wniosków o informację publiczną otrzymał urząd w 2012 roku
3.  Udostępnienie ewidencji wniosków o informację publiczną za 2011 rok. Jeżeli ewidencja prowadzona jest w formie elektronicznej, żądamy udostępnienia w postaci pliku w formacie dokumentu tekstowego lub arkusza kalkulacyjnego. Jeżeli ewidencja/rejestr nie jest prowadzony w formie elektronicznej, wnosimy o udostępnienie informacji w postaci skanu, z dokonaniem niezbędnych wyłączeń dotyczących ochrony prywatności wnioskujących osób.
4.  Udostępnienie ewidencji wniosków o informację publiczną za 2012 rok. Jeżeli ewidencja prowadzona jest w formie elektronicznej, żądamy udostępnienia w postaci pliku w formacie dokumentu tekstowego lub arkusza kalkulacyjnego. Jeżeli ewidencja/rejestr nie jest prowadzony w formie elektronicznej, wnosimy o udostępnienie informacji w postaci skanu, z dokonaniem niezbędnych wyłączeń dotyczących ochrony prywatności wnioskujących osób.

Dane, które można uzyskać dzięki masowej analizie obywatelskiej to:

*   Ile wniosków wpłynęło w 2011 roku? LICZBA
*   Ile wniosków wpłynęło w 2012 roku? LICZBA
*   Czy załączona została ewidencja wniosków za 2011 rok? TAK/NIE
*   Czy załączona została ewidencja wniosków za 2012 rok? TAK/NIE
*   Kiedy wniosek został zrealizowany? FORMAT DATY
*   Czy urząd twierdzi, że żądanie dotyczy informacji przetworzonej? odhaczenie jeśli tak
*   Czy za przygotowanie informacji zażądano opłaty/sugerowano opłatę? odhaczenie jeśli tak
*   Czy napisano, że konieczne jest przedłużenie czasu potrzebnego na odpowiedź? odhaczenie jeśli tak
*   Czy w tej gminie wystąpiła sytuacja braku ewidencji, ale w zamian pojawiły się skany wniosków? odhaczenie jeśli tak
*   Czy w tej gminie wystąpiła sytuacja braku ewidencji, ale w zamian w odpowiedzi pojawił się opis złożonych wniosków? odhaczenie jeśli tak
