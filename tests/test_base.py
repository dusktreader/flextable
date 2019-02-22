class TestSetTableMixin:
    def test_create_set(self, models):
        (Set, _) = models
        instance = Set.create(name="dummy", description="whatever")
        assert instance.name == "dummy"
        assert instance.description == "whatever"

    def test_update_set(self, models):
        (Set, _) = models
        instance = Set.create(name="dummy")
        instance.update(description="whatever")
        assert instance.name == "dummy"
        assert instance.description == "whatever"

    def test_delete_set(self, models):
        (Set, _) = models
        instance = Set.create(name="dummy")
        instance.delete()
        assert Set.query.filter_by(name="dummy").count() == 0


class TestFlexTableMixin:
    def test_base_keys(self, models):
        (_, Flex) = models
        assert sorted(Flex.base_keys()) == ["description", "id", "name"]

        instance = Flex(name="dummy")
        instance["foo"] = "bar"
        assert sorted(instance.base_keys()) == ["description", "id", "name"]

    def test___setitem__(self, models):
        (_, Flex) = models
        instance = Flex(name="dummy")
        instance["name"] = "idiot"
        assert instance.name == "idiot"
        instance["foo"] = "bar"
        assert instance.flex_data == {"foo": "bar"}

    def test___getitem__(self, models):
        (_, Flex) = models
        instance = Flex(name="dummy")
        instance["foo"] = "bar"
        assert instance["name"] == "dummy"
        assert instance["foo"] == "bar"

    def test_flex_keys(self, models):
        (_, Flex) = models

        instance = Flex(name="dummy")
        assert sorted(instance.flex_keys()) == []
        instance["foo"] = "bar"
        instance["baz"] = "bang"
        assert sorted(instance.flex_keys()) == ["baz", "foo"]

    def test_to_dict(self, models):
        (_, Flex) = models

        instance = Flex(name="dummy")
        instance["foo"] = "bar"
        instance["baz"] = "bang"
        assert instance.to_dict() == {
            "id": None,  # because it hasn't been mapped yet
            "name": "dummy",
            "description": None,
            "foo": "bar",
            "baz": "bang",
        }

    def test_create_flex(self, models):
        (_, Flex) = models
        instance = Flex.create(name="dummy", description="whatever", foo="bar")
        assert instance.name == "dummy"
        assert instance.description == "whatever"
        assert instance.flex_data == {"foo": "bar"}

    def test_update_flex(self, models):
        (_, Flex) = models
        instance = Flex.create(name="dummy")
        instance.update(foo="bar")
        assert instance.flex_data == {"foo": "bar"}

    def test_delete_flex(self, models):
        (_, Flex) = models
        instance = Flex.create(name="dummy")
        instance.delete()
        assert Flex.query.filter_by(name="dummy").count() == 0
