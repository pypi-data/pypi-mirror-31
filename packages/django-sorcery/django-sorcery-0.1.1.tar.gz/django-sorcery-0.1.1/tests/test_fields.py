# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.core.exceptions import ValidationError

from django_sorcery import fields

from .base import TestCase
from .models import CompositePkModel, Owner, VehicleType, db


class TestEnumField(TestCase):

    def test_to_python(self):
        field = fields.EnumField(enum_class=VehicleType)

        value = field.to_python(None)
        self.assertIsNone(value)

        value = field.to_python("car")
        self.assertEqual(value, VehicleType.car)

    def test_valid_value(self):
        value = fields.EnumField(enum_class=VehicleType).valid_value(None)
        self.assertFalse(value)

        value = fields.EnumField(enum_class=VehicleType, required=False).valid_value(None)
        self.assertTrue(value)

        value = fields.EnumField(enum_class=VehicleType, required=False).valid_value("car")
        self.assertFalse(value)

        value = fields.EnumField(enum_class=VehicleType, required=False).valid_value(VehicleType.car)
        self.assertTrue(value)


class TestModelChoiceField(TestCase):

    def setUp(self):
        super(TestModelChoiceField, self).setUp()
        db.add_all([Owner(first_name="first_name {}".format(i), last_name="last_name {}".format(i)) for i in range(10)])
        db.flush()

    def test_choices(self):

        field = fields.ModelChoiceField(Owner, db)

        self.assertListEqual(
            list(field.choices), [("", field.empty_label)] + [(owner.id, str(owner)) for owner in Owner.query]
        )

        field = fields.ModelChoiceField(Owner, db, required=True, initial=1)
        self.assertListEqual(list(field.choices), [(owner.id, str(owner)) for owner in Owner.query])

    def test_get_object(self):

        field = fields.ModelChoiceField(Owner, db)

        self.assertIsNone(field.get_object(None))

        owner = field.get_object(1)
        self.assertIsNotNone(owner)
        self.assertIsInstance(owner, Owner)

        with self.assertRaises(ValidationError) as ctx:
            field.get_object(100)

        self.assertEqual(
            ctx.exception.args,
            ("Select a valid choice. That choice is not one of the available choices.", "invalid_choice", None),
        )

    def test_to_python(self):

        field = fields.ModelChoiceField(Owner, db)
        owner = field.to_python(1)
        self.assertIsNotNone(owner)
        self.assertIsInstance(owner, Owner)

    def test_label_from_instance(self):
        field = fields.ModelChoiceField(Owner, db)

        self.assertEqual(
            field.label_from_instance(Owner.query.get(1)),
            "Owner(id=1, first_name='first_name 0', last_name='last_name 0')",
        )

    def test_prepare_instance_value(self):
        field = fields.ModelChoiceField(Owner, db)

        pks = field.prepare_instance_value(Owner.query.get(1))
        self.assertEqual(pks, 1)

    def test_prepare_instance_value_composite(self):
        field = fields.ModelChoiceField(CompositePkModel, db)

        pks = field.prepare_instance_value(CompositePkModel(id=1, pk="a"))
        self.assertDictEqual(pks, {"id": 1, "pk": "a"})

    def test_prepare_value(self):
        field = fields.ModelChoiceField(CompositePkModel, db)
        pks = field.prepare_value(CompositePkModel(id=1, pk="a"))
        self.assertDictEqual(pks, {"id": 1, "pk": "a"})

    def test_validate(self):
        field = fields.ModelChoiceField(Owner, db, required=True)

        self.assertIsNone(field.validate(1))

        with self.assertRaises(ValidationError):
            field.validate(None)


class TestModelMultipleChoiceField(TestCase):

    def setUp(self):
        super(TestModelMultipleChoiceField, self).setUp()
        db.add_all([Owner(first_name="first_name {}".format(i), last_name="last_name {}".format(i)) for i in range(10)])
        db.flush()

    def test_to_python(self):
        field = fields.ModelMultipleChoiceField(Owner, db)

        self.assertEqual(field.to_python(None), [])

        self.assertEqual(field.to_python([1, 2, 3]), [Owner.query.get(1), Owner.query.get(2), Owner.query.get(3)])

    def test_prepare_value(self):
        field = fields.ModelMultipleChoiceField(Owner, db)

        self.assertIsNone(field.prepare_value(None))

        self.assertEqual(field.prepare_value([Owner.query.get(1), Owner.query.get(2), Owner.query.get(3)]), [1, 2, 3])
