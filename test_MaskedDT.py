import unittest
import os
from typing import Any, List, Dict
from datetime import date

from datasurface.platforms.yellow.yellow_states import JobStatus
from datasurface.platforms.yellow.testing import BaseDTLocalTest, DBTTestArtifact


class TestMaskedCustomerGeneratorDBT(BaseDTLocalTest):
    """
    Test MaskedCustomerGenerator DBT Transformer locally.
    """

    def setUp(self) -> None:
        super().setUp()

        os.environ["test-db-cred_USER"] = "postgres"
        os.environ["test-db-cred_PASSWORD"] = "password"

        # The dbt project is in the same directory as this test
        dbt_project_path = os.path.dirname(__file__)

        # Setup with DBT artifact handler
        self.setup_from_transformer_module(
            module_path="transformer",
            credential_name="test_db_cred",
            artifact_handler=DBTTestArtifact(dbt_project_path)
        )

    def test_mask_customer_basic_workflow(self) -> None:
        """Test basic masking workflow: inject -> transform -> verify."""
        unmasked_data: List[Dict[str, Any]] = [
            {
                "id": "CUST001",
                "firstname": "alice",
                "lastname": "smith",
                "dob": date(1990, 1, 15),
                "email": "alice.smith@company.com",
                "phone": "555-123-4567",
                "primaryaddressid": "ADDR001",
                "billingaddressid": "ADDR001"
            }
        ]

        self.inject_data("customers", unmasked_data)

        # Run dbt transformer job
        status = self.run_dt_job()
        self.assertEqual(status, JobStatus.DONE, "DBT job should complete successfully")

        # Verify masked output
        output = self.get_output_data("customers")
        self.assertEqual(len(output), 1, "Should have exactly 1 masked record")

        masked_record = output[0]
        self.assertEqual(masked_record["id"], "CUST001")
        self.assertIn("***", masked_record["firstname"])
        self.assertIn("***", masked_record["lastname"])
        self.assertIn("***@", masked_record["email"])

    def test_mask_multiple_customers(self) -> None:
        """Test masking multiple customers in one batch."""
        batch_data: List[Dict[str, Any]] = [
            {
                "id": "CUST001",
                "firstname": "alice",
                "lastname": "smith",
                "dob": date(1990, 1, 15),
                "email": "alice.smith@example.com",
                "phone": "555-111-1111",
                "primaryaddressid": "ADDR001",
                "billingaddressid": "ADDR001"
            },
            {
                "id": "CUST002",
                "firstname": "bob",
                "lastname": "jones",
                "dob": date(1985, 5, 20),
                "email": "bob.jones@example.com",
                "phone": "555-222-2222",
                "primaryaddressid": "ADDR002",
                "billingaddressid": "ADDR002"
            }
        ]

        self.inject_data("customers", batch_data)
        self.assertEqual(self.run_dt_job(), JobStatus.DONE)

        output = self.get_output_data()
        self.assertEqual(len(output), 2)

        ids = {record["id"] for record in output}
        self.assertEqual(ids, {"CUST001", "CUST002"})

    def test_mask_null_values(self) -> None:
        """Test handling of NULL values."""
        batch_data: List[Dict[str, Any]] = [
            {
                "id": "CUST004",
                "firstname": "david",
                "lastname": "brown",
                "dob": date(1988, 3, 25),
                "email": None,
                "phone": None,
                "primaryaddressid": None,
                "billingaddressid": None
            }
        ]

        self.inject_data("customers", batch_data)
        self.assertEqual(self.run_dt_job(), JobStatus.DONE)

        output = self.get_output_data()
        self.assertEqual(len(output), 1)
        masked = output[0]
        self.assertIsNone(masked["email"])


if __name__ == "__main__":
    unittest.main()
