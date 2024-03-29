from django_filters.filters import Filter
from django.forms.fields import MultipleChoiceField


class MultipleValueField(MultipleChoiceField):
    """
    Поле для выбора нескольких значений.
    """

    def __init__(self, *args, field_class, **kwargs):
        """
        Инициализация поля.

        :param field_class: Класс поля, используемый внутри MultipleValueField.
        """
        self.inner_field = field_class()
        super().__init__(*args, **kwargs)

    def valid_value(self, value):
        """
        Проверка на валидность значения.

        :param value: Проверяемое значение.
        :return: Результат проверки.
        """
        return self.inner_field.validate(value)

    def clean(self, values):
        """
        Очистка значений.

        :param values: Значения для очистки.
        :return: Очищенные значения.
        """
        return values and [self.inner_field.clean(value) for value in values]


class MultipleValueFilter(Filter):
    """
    Фильтр для выбора нескольких значений.
    """
    field_class = MultipleValueField

    def __init__(self, *args, field_class, **kwargs):
        """
        Инициализация фильтра.

        :param field_class: Класс поля, используемый внутри MultipleValueFilter.
        """
        kwargs.setdefault('lookup_expr', 'in')
        super().__init__(*args, field_class=field_class, **kwargs)
