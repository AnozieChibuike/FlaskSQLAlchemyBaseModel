# test_base_model.py
import unittest
from datetime import datetime
from .app import create_app

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from flasksqlalchemybasemodel import db, BaseModel

class TestModel(BaseModel):
    __tablename__ = 'test_model'
    name = db.Column(db.String(50), nullable=False)

class BaseModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_instance(self):
        instance = TestModel(name="Test")
        instance.save()
        self.assertIsNotNone(instance.id)
        self.assertEqual(instance.name, "Test")
        self.assertTrue(isinstance(instance.created_at, datetime))
        self.assertTrue(isinstance(instance.updated_at, datetime))

    def test_update_instance(self):
        instance = TestModel(name="Test")
        instance.save()
        old_updated_at = instance.updated_at

        instance.update({"name": "Updated Test"})
        updated_instance = TestModel.get(instance.id)

        self.assertEqual(updated_instance.name, "Updated Test")
        self.assertNotEqual(updated_instance.updated_at, old_updated_at)

    def test_delete_instance(self):
        instance = TestModel(name="Test")
        instance.save()
        instance_id = instance.id

        instance.delete()
        self.assertIsNone(TestModel.get(instance_id))

    def test_to_dict(self):
        instance = TestModel(name="Test")
        instance.save()
        instance_dict = instance.to_dict()
        
        self.assertEqual(instance_dict["name"], "Test")
        self.assertEqual(instance_dict["id"], instance.id)
        self.assertTrue("created_at" in instance_dict)
        self.assertTrue("updated_at" in instance_dict)

    def test_all_method(self):
        instance1 = TestModel(name="Test1")
        instance2 = TestModel(name="Test2")
        instance1.save()
        instance2.save()

        all_instances = TestModel.all()
        self.assertEqual(len(all_instances), 2)

    def test_get_method(self):
        instance = TestModel(name="Test")
        instance.save()

        retrieved_instance = TestModel.get(instance.id)
        self.assertIsNotNone(retrieved_instance)
        self.assertEqual(retrieved_instance.name, "Test")

    def test_filter_one_method(self):
        instance = TestModel(name="Test")
        instance.save()

        filtered_instance = TestModel.filter_one(name="Test")
        self.assertIsNotNone(filtered_instance)
        self.assertEqual(filtered_instance.name, "Test")

    def test_filter_all_method(self):
        instance1 = TestModel(name="Test1")
        instance2 = TestModel(name="Test2")
        instance1.save()
        instance2.save()

        filtered_instances = TestModel.filter_all(name="Test1")
        self.assertEqual(len(filtered_instances), 1)
        self.assertEqual(filtered_instances[0].name, "Test1")

    def test_filter_and_count_all_method(self):
        instance1 = TestModel(name="Test1")
        instance2 = TestModel(name="Test2")
        instance1.save()
        instance2.save()

        count = TestModel.filter_and_count_all(name="Test1")
        self.assertEqual(count, 1)

    def test_count_all_method(self):
        instance1 = TestModel(name="Test1")
        instance2 = TestModel(name="Test2")
        instance1.save()
        instance2.save()

        count = TestModel.count_all()
        self.assertEqual(count, 2)

    def test_exists_method(self):
        instance = TestModel(name="Test")
        instance.save()

        exists = TestModel.exists(name="Test")
        self.assertTrue(exists)

    def test_paginate_method(self):
        for i in range(1, 21):
            instance = TestModel(name=f"Test{i}")
            instance.save()

        paginated_results = TestModel.paginate(page=1, per_page=5)
        self.assertEqual(len(paginated_results["items"]), 5)
        self.assertEqual(paginated_results["total"], 20)
        self.assertEqual(paginated_results["pages"], 4)
        self.assertEqual(paginated_results["page"], 1)
        self.assertEqual(paginated_results["per_page"], 5)

if __name__ == '__main__':
    unittest.main()
