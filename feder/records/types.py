from abc import abstractmethod, ABCMeta


class BaseRecordType:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_verbose_name(self, obj):
        pass

    @abstractmethod
    def get_verbose_name_plural(self, obj):
        pass

    @abstractmethod
    def get_template_milestone_item(self, obj):
        pass

    @abstractmethod
    def get_template_content_item(self, obj):
        pass


class CommonRecordType(BaseRecordType):
    def __init__(self, model_cls):
        self.model_cls = model_cls

    def get_verbose_name(self, obj):
        return self.model_cls._meta.verbose_name

    def get_verbose_name_plural(self, obj):
        return self.model_cls._meta.verbose_name_plural

    def get_template_milestone_item(self, obj):
        return "{}/_{}{}.html".format(
            self.model_cls._meta.app_label,
            self.model_cls._meta.model_name,
            "_milestone_item",
        )

    def get_template_content_item(self, obj):
        return "{}/_{}{}.html".format(
            self.model_cls._meta.app_label,
            self.model_cls._meta.model_name,
            "_content_item",
        )
