****************************
Przygotowanie bazy adresowej
****************************

Rzetelne funkcjonowanie systemu Obywatelskiego Fedrowania Danych rozumiane w szczególności jako przystępna nawigacja, pomimo rozrostu systemu, wymaga odpowiedniej jakości bazy danych. Wymaganymi danymi dla każdej instytucji jest co najmniej:

* pełna i kompletna nazwa instytucji - identyfikacji instytucji przez użytkowników strony,
* adres e-mail instytucji - korespondencji z instytucją,
* numer identyfikacyjny REGON - weryfikacji unikalności instytucji, a także weryfikacji zmian w strukturze instytucji (likwidacja, przekształcenie itd.)
* kod TERC (rejestr podziału terytorialnego) z bazy TERYT - nawigacja według regionu.

Gromadzone są także:

* tagi, które pozwalają na przypisywanie jednej lub kilku kategorii do instytucij np. marszałkowie, lasy państwowe, dyrekcja lasów państwowych, sądy,
* wyciąg z rejestru REGON,
* odwołanie do instytucji nadrzędnych,
* inne informacje, które mogą zostać w przyszłości wykorzystane.

Wskazuje, że Stowarzyszenie Sieć Obywatelska Watchdog Polska ma zapewniony dostęp do rejestru REGON na podstawie numeru REGON/NIP/KRS poprzez API. Kluczami dostępowymi dysponuje Administrator Bezpieczeństwa Informacji.

Nie mamy możliwości przeszukiwania tej bazy danych na podstawie regionów, ani nazw instytucji, ani ich kategorii. Stowarzyszenie ma jednak możliwość wyszukania nazwy instytucji w Google, pobrania wszystkich cyfr z nadzieją, że wśród nich będzie numer REGON, co pozwoli uzupełnić lokalną kopie rejestru REGON, a następnie przeszukiwania według nazwy wcześniej pobrane instytucje, które były przedmiotem odrębnych analiz. Pozwoli to opracować częściowe zestawienie, które może okazać się pomocne w dalszych pracach.

Rejestr REGON pozwala na wyszukiwanie po numerze NIP i KRS, zatem kod REGON nie wymaga uzupełnienia w przypadku obecności kodu NIP/KRS. Mogą one być stosowane wymiennie.

Mając na względzie powyższe:

* pełna i kompletna nazwa instytucji - rejestr REGON pozwala na dostarczenie podpowiedzi w tym zakresie na podstawie numeru REGON, lecz rejestr REGON nie jest w tym zakresie wystarczający, gdyż w wielu wypadkach wprowadzone nazwy nie spełniają poniżej przedstawionych wymogów,
* adres e-mail instytucji - rejestr REGON pozwala czasem na dostarczenie informacji w tym zakresie, nie zawsze aktualnych i kompletnych,
* numer REGON - rejestr REGON pozwala na uzupełnienie informacji na podstawie numerów NIP/KRS i można dostarczyć podpowiedzi na podstawie wcześniej pobranych rekordów bazy REGON,
* numer TERC (rejestr podziału terytorialnego) z bazy TERYT - rejestr REGON pozwala w pełni na uzupełnienie tych informacji.

Format nazw instytucji
----------------------

Nie akceptowalne w polu nazwa instytucji jest występowanie samych nazw miejscowości, gdzie dany podmiot ma siedzibę. Nazwa instytucji regionalnych winna składać się z oznaczenia ``[kategoria / nazwa] [w/we] [miejscowość odmieniony jako miejscownik]``. Niedopuszczalne jest stosowanie w nazwie danej instytucji nazw innych instytucji np. instytucji nadrzędnej.

Uwagi na temat rejestru REGON
-----------------------------

Rejestr REGON:

* służy osiągnięciu spójności identyfikacyjnej podmiotów gospodarki narodowej wpisywanych do innych urzędowych rejestrów i systemów informacyjnych administracji publicznej,
* służy jednolitości opisów stosowanych w nomenklaturze pojęciowej i klasyfikacyjnej we wszystkich urzędowych rejestrach i systemach informacyjnych administracji publicznej,
* dostarcza ogólnej charakterystyki działających w gospodarce narodowej podmiotów w przekrojach: terytorialnym, własnościowym, rodzajów działalności, form prawnych itp.,
* umożliwia sporządzanie wykazu adresów działających podmiotów,
* jest podstawą do tworzenia baz i banków danych o podmiotach gospodarki narodowej,
* stanowi główne źródło zasilania bazy jednostek wybieranych do badań statystycznych.

Dostęp do rejestru REGON możliwy jest poprzez `oficjalną internetową wyszukiwarkę <https://wyszukiwarkaregon.stat.gov.pl/appBIR/index.aspx>`_.

Numer identyfikacyjny REGON podmiotu gospodarki narodowej skreślonego z rejestru REGON jest przechowywany w zbiorze historycznym i nie jest wykorzystywany do identyfikacji innego podmiotu.

Numer identyfikacyjny REGON podmiotu gospodarki narodowej składa się z dziewięciu cyfr, które nie mogą mieć ukrytego lub jawnego charakteru znaczącego, określającego pewne cechy podmiotu, przy czym osiem pierwszych cyfr stanowi liczbę porządkową, a dziewiąta – cyfrę kontrolną.

Numer identyfikacyjny REGON jednostki lokalnej składa się z czternastu cyfr, przy czym dziewięć pierwszych cyfr jest tożsame z numerem identyfikacyjnym REGON osoby prawnej, jednostki organizacyjnej niemającej osobowości prawnej lub osoby fizycznej prowadzącej działalność gospodarczą, cztery kolejne cyfry są liczbą porządkową przypisaną jednostce lokalnej, a czternasta cyfra – cyfrą kontrolną.

Szczegółowe informacje w zakresie funkcjonowania rejestru są przedstawione w:

* `Informacje ogólne – Biuletyn Informacji Publicznej Głównego Urzędu Statystycznego <http://bip.stat.gov.pl/dzialalnosc-statystyki-publicznej/rejestr-regon/informacje-ogolne/>`_
* `Rozporządzenie Rady Ministrów z dnia 30 listopada 2015 r. w sprawie sposobu i metodologii prowadzenia i aktualizacji krajowego rejestru urzędowego podmiotów gospodarki narodowej, wzorów wniosków, ankiet i zaświadczeń (Dz. U. poz. 2009, z późn. zm.) <http://bip.stat.gov.pl/download/gfx/bip/pl/defaultstronaopisowa/446/1/1/rozporzadzenie_regon_tekst_ujednolicony.doc>`_
