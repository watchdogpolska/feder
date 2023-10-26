from langchain.prompts import PromptTemplate

letter_evaluation_intro = PromptTemplate.from_template(
    """
    Do {institution} wysłano wniosek o informację publiczną  o treści:
    ```{monitoring_question}```.
    """
)

letter_categorization = PromptTemplate.from_template(
    """{intro}
    Oceń odpowiedź z {institution} podaną na końcu, przypisując ją do jednej z kategorii
    z listy poniżej wybierając odpowiednią literę wraz z opisem:
    ```
    A) email jest odpowiedzią z {institution} i zawiera odpowiedzi na pytania z
        wniosku o informację publiczną.
    B) email jest odpowiedzią z {institution} i zawiera odmowę odpowiedzi na
        pytania z wniosku o informację publiczną.
    C) email jest odpowiedzią z {institution} i zawiera informację o
        przedłużeniu terminu na odpowiedź.
    D) email jest potwierdzeniem dostarczenia lub otwarcia maila z {institution}
        i nie zawiera odpowiedzi na pytania z wniosku o informację publiczną.
    E) email jest odpowiedzią z innej instytucji lub na inny wniosek.
    F) email nie jest odpowiedzią z {institution} i jest spamem.
    G) nie można ustalić kategorii odpowiedzi.
    ```
    Odpowiedź z {institution}, jako połączony tekst maila i załączników:
    ```{monitoring_response}```.
    """,
)

letter_response_formatting = PromptTemplate.from_template(
    """{intro}
    Przeanalizuj odpowiedź z {institution} podaną na końcu, i uzupełnij odpowiedzi
    w ujednoliconej formie dokumentu informacyjnego zawierającego listę
    pytań i odpowiedzi w postaci:
    Pytanie: "pytanie z wniosku o informację publiczną"
    Odpowiedź: "odpowiedź z maila"

    Odpowiedź z {institution}, jako połączony tekst maila i załączników:
    ```{monitoring_response}```.
    """,
)

monitoring_response_normalized_template = PromptTemplate.from_template(
    """
    Przeanalizuj podny poniżej tekst i sprawdź czy jest wnioskiem o udostępnienie
    informacji publicznej. Jeśli tak to zbuduj template do ujednolicenia treści
    odpowiedzi w postaci json:
    {{
        "1": {{"Pytanie":"treść pytania 1", "Odpowiedź":""}},
        "2": {{"Pytanie":"treść pytania 2", "Odpowiedź":""}}
    }}
    Jako klucze w jsonie użyj numerów pytań z zapytania o informację publiczną, a jako
    wartości pytania, treść pytań wraz z oznaczeniem w zapytaniu. W przypadku braku
    oznaczeń pytań w zapytaniu ponumeruj je po kolei od 1.

    Na przykład, rezultatem z treści wniosku o informację publiczną:
    ```
    <br />
    3.&nbsp;&nbsp;Czy dane w poszczeg&oacute;lnych wydziałach urzędu wprowadzane
       są do państwowych system&oacute;w? <br /><br />
    a) Jeśli tak, to jakich? <br />
    b) Jeśli tak, to z kt&oacute;rych system&oacute;w urząd może pobrać dane dla
        swoich cel&oacute;w? <br /><br />
    4. Czy systemy urzędu są zintegrowane z innymi systemami samorządowymi lub
       rządowymi? Jeżeli tak, prosimy o podanie nazw system&oacute;w. <br />
    ```
    powinnien być json:
    {{
        "3": {{"Pytanie":"3. Czy dane w poszczególnych wydziałach urzędu wprowadzane
                         są do państwowych systemów?",
              "Odpowiedź":""}},
        "3a": {{"Pytanie":"a) Jeśli tak, to jakich?",
               "Odpowiedź":""}},
        "4": {{"Pytanie":"4. Czy systemy urzędu są zintegrowane z innymi systemami
                         samorządowymi lub rządowymi? Jeżeli tak, prosimy o podanie
                         nazw systemów.",
              "Odpowiedź":""}}
    }}
    W odpowiedzi podaj tylko poprawnie sformatowany json, bez żadnych dodatkowych
    wyjaśnień.
    Jeśli tekst nie jest wnioskiem o udostępnienime informacji publicznej, lecz jest
    informacją wysłaną do instytucji publicznej to odpowiedzią powinien być pusty
    json: {{}}.
    Tekst do analizy:
    ```{monitoring_template}```.
    """,
    template_format="f-string",
)
