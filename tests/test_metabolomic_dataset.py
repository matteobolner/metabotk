import pytest
from metabotk.metabolomic_dataset import MetabolomicDataset


class TestMetabolomicDataset:
    def test_initialization(self):
        person = MetabolomicDataset(
            data,
            sample_metadata,
            chemical_annotation,
            sample_id_column,
            metabolite_id_column,
        )
        assert person.get_name() == "Alice"
        assert person.get_age() == 30

    def test_setter_getter_name(self):
        person = Person("Alice", 30)
        person.set_name("Bob")
        assert person.get_name() == "Bob"

    def test_setter_getter_age(self):
        person = Person("Alice", 30)
        person.set_age(35)
        assert person.get_age() == 35

    def test_getter_before_setter(self):
        person = Person("Alice", 30)
        assert person.get_name() == "Alice"
        assert person.get_age() == 30

    def test_setter_update_values(self):
        person = Person("Alice", 30)
        person.set_name("Charlie")
        person.set_age(40)
        assert person.get_name() == "Charlie"
        assert person.get_age() == 40
