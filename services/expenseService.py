import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from models.Expense import Expense
from models.Supplier import Supplier

class ExpenseService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_expenses(self) -> List[Expense]:
        """Obtiene todos los gastos con sus relaciones cargadas"""
        return self.db.query(Expense).options(
            joinedload(Expense.supplier)
        ).all()

    def create_expense(self, expense_data: dict) -> Expense:
        try:
            # Crear gasto
            expense = Expense(
                amount=float(expense_data['amount']),
                description=str(expense_data['description']),
                category=str(expense_data['category']),
                supplier_id=expense_data.get('supplier_id')  # Puede ser None
            )

            self.db.add(expense)
            self.db.commit()
            self.db.refresh(expense)
            return expense

        except Exception as e:
            self.db.rollback()
            logging.error(f"Error creating expense: {str(e)}")
            raise

    def get_expense_by_id(self, expense_id: int) -> Optional[Expense]:
        """Obtiene un gasto por su ID"""
        return self.db.query(Expense).filter(Expense.id == expense_id).first()

    def get_expenses_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Expense]:
        """Obtiene los gastos en un rango de fechas"""
        return self.db.query(Expense).filter(
            Expense.date >= start_date,
            Expense.date <= end_date
        ).all()

    def get_total_expenses_amount(self, start_date: datetime, end_date: datetime) -> float:
        """Calcula el total de gastos en un rango de fechas"""
        expenses = self.get_expenses_by_date_range(start_date, end_date)
        return sum(expense.amount for expense in expenses)
    
    def get_expenses_by_category(self, category: str) -> List[Expense]:
        """Obtiene los gastos por categoría"""
        return self.db.query(Expense).filter(Expense.category == category).all()
    
    def get_expenses_by_supplier(self, supplier_id: int) -> List[Expense]:
        """Obtiene los gastos por proveedor"""
        return self.db.query(Expense).filter(Expense.supplier_id == supplier_id).all()
    
    def update_expense(self, expense_id: int, expense_data: dict) -> Optional[Expense]:
        """Actualiza un gasto existente"""
        expense = self.get_expense_by_id(expense_id)
        if expense:
            for key, value in expense_data.items():
                setattr(expense, key, value)
            self.db.commit()
            self.db.refresh(expense)
        return expense
    
    def delete_expense(self, expense_id: int) -> bool:
        """Elimina un gasto"""
        expense = self.get_expense_by_id(expense_id)
        if expense:
            self.db.delete(expense)
            self.db.commit()
            return True
        return False 