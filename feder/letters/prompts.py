def letter_evaluation_prompt(monitoring_question="", institution="", response=""):
    instruction = f"""
            W odpowiedzi na wniosek o informację publiczną do {institution}, o treści:
            ```{monitoring_question}```,
            otrzymano email z załącznikami o treści:
            ```{response}```.
            """
    prompts = {
        "q_1": f"""{instruction}
            Oceń otrzymany email z załącznikami i przypisz go do jednej z kategorii,
            z listy poniżej wybierając odpowiednią literę wraz z opisem:
            ```
            A) email jest odpowiedzią z {institution} i zawiera odpowiedzi na pytania z
                wniosku o informację publiczną.
            B) email jest odpowiedzią z {institution} i zawiera odmowę odpowiedzi na
                pytania z wniosku o informację publiczną.
            B1) email jest odpowiedzią z {institution} i zawiera informację o przedłużeniu 
                terminu na odpowiedź.
            C) email jest potwierdzeniem dostarczenia lub otwarcia maila z {institution}
                i nie zawiera odpowiedzi na pytania z wniosku o informację publiczną.
            D) email nie jest odpowiedzią z {institution} i jest spamem.
            E) nie można ustalić kategorii odpowiedzi.
            ```
            """,
        "q_2": f"""{instruction}
            Oceń otrzymany email z załącznikami i podaj oznaczenia pytań z wniosku o
            informację publiczną bez ich treści, na które udzielono odpowiedzi oraz
            numery pytań z wniosku na które odmówiono udzielenia odpowiedzi. Osobno podaj
            oznaczenia pytań dla których poproszono o wydłużenie terminu na odpowiedź.
            """,
    }
    return prompts
