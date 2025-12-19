from typing import List
from datasurface.md import Dataset, Datastore, DDLColumn, DDLTable, PlainTextDocumentation
from datasurface.md import NullableStatus, PrimaryKeyStatus, VarChar, Date
from datasurface.md.policy import SimpleDC, SimpleDCTypes
from datasurface.md.containers import TestCaptureMetaData


def defineInputDatasets() -> List[Datastore]:
    return [
        Datastore(
            "Store1",
            documentation=PlainTextDocumentation("Test datastore"),
            capture_metadata=TestCaptureMetaData(),
            datasets=[
                Dataset(
                    "customers",
                    schema=DDLTable(
                        columns=[
                            DDLColumn("id", VarChar(20), nullable=NullableStatus.NOT_NULLABLE, primary_key=PrimaryKeyStatus.PK),
                            DDLColumn("firstname", VarChar(100), nullable=NullableStatus.NOT_NULLABLE),
                            DDLColumn("lastname", VarChar(100), nullable=NullableStatus.NOT_NULLABLE),
                            DDLColumn("dob", Date(), nullable=NullableStatus.NOT_NULLABLE),
                            DDLColumn("email", VarChar(100)),
                            DDLColumn("phone", VarChar(100)),
                            DDLColumn("primaryaddressid", VarChar(20)),
                            DDLColumn("billingaddressid", VarChar(20))
                        ]
                    ),
                    classifications=[SimpleDC(SimpleDCTypes.CPI, "Customer")]
                )
            ]
        ),
    ]


def defineOutputDatastore() -> Datastore:
    return Datastore(
        name="MaskedCustomersDBT",
        documentation=None,
        datasets=[
            Dataset(
                "customers",
                schema=DDLTable(
                    columns=[
                        DDLColumn("id", VarChar(20), nullable=NullableStatus.NOT_NULLABLE,
                                  primary_key=PrimaryKeyStatus.PK),
                        DDLColumn("firstname", VarChar(100), nullable=NullableStatus.NOT_NULLABLE),
                        DDLColumn("lastname", VarChar(100), nullable=NullableStatus.NOT_NULLABLE),
                        DDLColumn("dob", Date(), nullable=NullableStatus.NOT_NULLABLE),
                        DDLColumn("email", VarChar(100)),
                        DDLColumn("phone", VarChar(100)),
                        DDLColumn("primaryaddressid", VarChar(20)),
                        DDLColumn("billingaddressid", VarChar(20))
                    ]
                ),
                classifications=[SimpleDC(SimpleDCTypes.PUB, "Customer")]
            )
        ]
    )
