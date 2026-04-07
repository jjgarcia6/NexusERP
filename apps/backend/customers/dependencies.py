from __future__ import annotations

from core.database import get_database
from customers.repositories.customer_repository import CustomerRepository
from customers.services.customer_service import CustomerService


def get_customer_service() -> CustomerService:
    database = get_database()
    customer_repository = CustomerRepository(database)
    return CustomerService(customer_repository)
