"""
These meta-datasources operate on :class:`revscoring.Datasource`'s that
return `list`'s of items and produce frequency tables.

.. autoclass:: revscoring.datasources.meta.frequencies.table

.. autoclass:: revscoring.datasources.meta.frequencies.delta

.. autoclass:: revscoring.datasources.meta.frequencies.prop_delta

.. autoclass:: revscoring.datasources.meta.frequencies.positive

.. autoclass:: revscoring.datasources.meta.frequencies.negative
"""
from ..datasource import Datasource


class table(Datasource):
    """
    Generates a frequency table for a list of items generated by another
    datasource.

    :Parameters:
        items_datasource : :class:`revscoring.Datasource`
            A datasource that generates a list of some `hashable` item
        name : `str`
            A name for the datasource.
    """

    def __init__(self, items_datasource, name=None):
        name = self._format_name(name, [items_datasource])
        super().__init__(name, self.process,
                         depends_on=[items_datasource])

    def process(self, items):

        freq = {}
        for item in items:
            if item in freq:
                freq[item] += 1
            else:
                freq[item] = 1

        return freq


class delta(Datasource):
    """
    Generates a frequency table diff by comparing two frequency tables.

    :Parameters:
        old_ft_datasource : :class:`revscoring.Datasource`
            A frequency table datasource
        new_ft_datasource : :class:`revscoring.Datasource`
            A frequency table datasource
        name : `str`
            A name for the datasource.
    """

    def __init__(self, old_ft_datasource, new_ft_datasource, name=None):
        name = self._format_name(name, [old_ft_datasource, new_ft_datasource])
        super().__init__(name, self.process,
                         depends_on=[old_ft_datasource, new_ft_datasource])

    def process(self, old_ft, new_tf):
        old_ft = old_ft or {}

        delta_table = {}
        for item, new_count in new_tf.items():
            old_count = old_ft.get(item, 0)
            if new_count != old_count:
                delta_table[item] = new_count - old_count

        for item in old_ft.keys() - new_tf.keys():
            delta_table[item] = old_ft[item] * -1

        return delta_table


class prop_delta(Datasource):
    """
    Generates a proportional frequency table diff by comparing a
    frequency table diff with an old frequency table.

    :Parameters:
        old_ft_datasource : :class:`revscoring.Datasource`
            A frequency table datasource
        new_ft_datasource : :class:`revscoring.Datasource`
            A frequency table datasource
        name : `str`
            A name for the datasource.
    """

    def __init__(self, old_ft_datasource, delta_datasource, name=None):
        name = self._format_name(name, [old_ft_datasource, delta_datasource])
        super().__init__(name, self.process,
                         depends_on=[old_ft_datasource, delta_datasource])

    def process(self, old_tf, ft_delta):
        prop_delta = {}
        for item, delta in ft_delta.items():
            if delta > 0:
                prop_delta[item] = delta / (old_tf.get(item, 0) + 1)
            else:
                prop_delta[item] = delta / old_tf[item]

        return prop_delta


class positive(Datasource):
    """
    Filters a table (counts, delta, prop_delta, etc.) for positive values.

    :Parameters:
        table_datasource : :class:`revscoring.Datasource`
            A frequency table datasource
        name : `str`
            A name for the datasource.
    """

    def __init__(self, table_datasource, name=None):
        name = self._format_name(name, [table_datasource])
        super().__init__(name, self.process,
                         depends_on=[table_datasource])

    def process(self, table):
        return {k: value for k, value in table.items() if value > 0}


class negative(Datasource):
    """
    Filters a table (counts, delta, prop_delta, etc.) for negative values.

    :Parameters:
        table_datasource : :class:`revscoring.Datasource`
            A frequency table datasource
        absolute : `bool`
            Make negative values positive
        name : `str`
            A name for the datasource.
    """

    def __init__(self, table_datasource, absolute=False, name=None):
        name = self._format_name(name, [table_datasource])
        super().__init__(name, self.process,
                         depends_on=[table_datasource])
        self.absolute = absolute

    def process(self, table):
        if self.absolute:
            return {k: abs(value) for k, value in table.items() if value < 0}
        else:
            return {k: value for k, value in table.items() if value < 0}
