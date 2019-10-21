from django.conf import settings

DEFAULT_MODULATOR = [
    "feder.questionaries.modulator.JSTModulator",
    "feder.questionaries.modulator.IntegerModulator",
    "feder.questionaries.modulator.ChoiceModulator",
    "feder.questionaries.modulator.CharModulator",
    "feder.questionaries.modulator.LetterChoiceModulator",
    "feder.questionaries.modulator.DateModulator",
    "feder.questionaries.modulator.EmailModulator",
]

MODULATORS_LIST = getattr(settings, "QUESTIONARIES_MODULATOR", DEFAULT_MODULATOR)
