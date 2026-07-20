from enum import Enum


class WorkflowStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ArtifactStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ColumnSemanticType(str, Enum):
    UNKNOWN = "UNKNOWN"

    CUSTOMER_ID = "CUSTOMER_ID"
    PRODUCT_ID = "PRODUCT_ID"
    TRANSACTION_ID = "TRANSACTION_ID"

    DATE = "DATE"

    SALES_AMOUNT = "SALES_AMOUNT"
    QUANTITY = "QUANTITY"
    PRICE = "PRICE"

    STORE = "STORE"
    REGION = "REGION"