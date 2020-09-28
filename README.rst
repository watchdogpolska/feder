 .. image:: https://coveralls.io/repos/watchdogpolska/feder/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/watchdogpolska/feder?branch=master

 .. image:: https://github.com/watchdogpolska/feder/workflows/Python%20package/badge.svg
    :target: https://github.com/watchdogpolska/feder/actions?workflow=Python+package

 .. image:: https://img.shields.io/github/license/watchdogpolska/feder.svg

 .. image:: https://david-dm.org/watchdogpolska/feder/dev-status.svg
     :target: https://david-dm.org/watchdogpolska/feder#info=devDependencies
     :alt: devDependency Status

Feder
=====

Mechanizm do automatycznego wysyłania wniosków o informację do dużej liczby podmiotów, automatycznego przyjmowania odpowiedzi, udostępnienia otrzymanych odpowiedzi do analizy pod wybranym kątem przez masowo angażowanych do tego zadania obywateli oraz  upubliczniania zweryfikowanych odpowiedzi i zestawień uzyskanych danych.

Statyczna kontrola kodu
-----------------------

Statyczna kontrola kodu w projekcie służy do sprawdzenia, czy kod spełnia określone standardy jakości.

Wszystkie sprawdzenia kodu statycznego można uruchamiać za pomocą [pre-commit run](https://pre-commit.com/). Są one
także weryfikowane w środowisku [GitHub Actions](https://github.com/watchdogpolska/feder/actions), przy każdej
propozycji zmian zawartości repozytorium.

W celu instalacji narzędzia do statycznej kontroli kodu, należy wykonać:

```
pip install -r requirements/dev.txt
```

W celu wykonania kontroli statycznej kodu, należy wykonać:

```bash
git add .
make lint
```

Aby włączyć automatyczne sprawdzanie kodu przed stworzeniem zmiany (`commit`), należy wykonać:

```bash
pre-commit install
```
