import autocomplete_light
from models import Institution, Tag


autocomplete_light.register(Institution,
    search_fields=['name', ],
)


autocomplete_light.register(Tag,
    search_fields=['name', ],
)
