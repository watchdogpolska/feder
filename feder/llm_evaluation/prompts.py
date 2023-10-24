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

letter_response_answers_evaluation = PromptTemplate.from_template(
    """{intro}
    Oceń otrzymany email z załącznikami i podaj oznaczenia pytań z wniosku o
    informację publiczną bez ich treści, na które udzielono odpowiedzi oraz
    numery pytań z wniosku na które odmówiono udzielenia odpowiedzi. Osobno
    podaj oznaczenia pytań dla których poproszono o wydłużenie terminu na
    odpowiedź.
    """,
)

letter_response_formatting = PromptTemplate.from_template(
    """{intro}
    Zbuduj ujednoliconą formę dokumentu informacyjnego zawierającego listę
    pytań i odpowiedzi w postaci:
    Pytanie: "pytanie z wniosku o informację publiczną"
    Odpowiedź: "odpowiedź z maila"
    """,
)
