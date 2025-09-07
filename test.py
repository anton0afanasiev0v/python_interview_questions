from datetime import datetime
from typing import Dict, List
from decimal import Decimal
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Employee:
    id: int
    base_salary: Decimal
    department: str
    position: str = ""
    years_of_experience: int = 0
    sales_amount: Decimal = Decimal('0')
    overtime: int = 0
    vacation_days: int = 0
    team_size: int = 0


@dataclass
class SalaryCalculation:
    base_salary: Decimal
    bonus: Decimal
    overtime_pay: Decimal
    vacation_pay: Decimal
    total_before_deductions: Decimal
    tax: Decimal
    social_security: Decimal
    medicare: Decimal
    total_deductions: Decimal
    final_salary: Decimal
    calculation_date: str


class BonusCalculator(ABC):
    @abstractmethod
    def calculate_bonus(self, employee: Employee) -> Decimal:
        pass


class SalesBonusCalculator(BonusCalculator):
    def calculate_bonus(self, employee: Employee) -> Decimal:
        if employee.sales_amount > 100000:
            bonus = employee.sales_amount * Decimal('0.15')
            if employee.years_of_experience > 5:
                bonus += employee.sales_amount * Decimal('0.05')
        elif 50000 <= employee.sales_amount <= 100000:
            bonus = employee.sales_amount * Decimal('0.10')
            if employee.position.lower() == 'senior':
                bonus += employee.sales_amount * Decimal('0.02')
        else:
            bonus = employee.sales_amount * Decimal('0.05')
        return bonus


class DevelopmentBonusCalculator(BonusCalculator):
    def calculate_bonus(self, employee: Employee) -> Decimal:
        if employee.position.lower() == 'senior':
            bonus = employee.base_salary * Decimal('0.30')
            if employee.years_of_experience > 3:
                bonus += employee.base_salary * Decimal('0.10')
        elif employee.position.lower() == 'middle':
            bonus = employee.base_salary * Decimal('0.20')
            if employee.years_of_experience > 3:
                bonus += employee.base_salary * Decimal('0.05')
        else:
            bonus = employee.base_salary * Decimal('0.10')
        return bonus


class ManagementBonusCalculator(BonusCalculator):
    def calculate_bonus(self, employee: Employee) -> Decimal:
        if employee.team_size > 10:
            return employee.base_salary * Decimal('0.25')
        elif 5 <= employee.team_size <= 10:
            return employee.base_salary * Decimal('0.15')
        else:
            return employee.base_salary * Decimal('0.10')


class DefaultBonusCalculator(BonusCalculator):
    def calculate_bonus(self, employee: Employee) -> Decimal:
        return Decimal('0')


class BonusCalculatorFactory:
    @staticmethod
    def get_calculator(department: str) -> BonusCalculator:
        calculators = {
            'sales': SalesBonusCalculator(),
            'development': DevelopmentBonusCalculator(),
            'management': ManagementBonusCalculator()
        }
        return calculators.get(department.lower(), DefaultBonusCalculator())


class TaxCalculator:
    @staticmethod
    def calculate_tax(amount: Decimal) -> Decimal:
        if amount > 100000:
            return amount * Decimal('0.35')
        elif amount > 50000:
            return amount * Decimal('0.25')
        else:
            return amount * Decimal('0.20')
    
    @staticmethod
    def calculate_social_security(amount: Decimal) -> Decimal:
        return amount * Decimal('0.065')
    
    @staticmethod
    def calculate_medicare(amount: Decimal) -> Decimal:
        return amount * Decimal('0.0145')


class OvertimeCalculator:
    @staticmethod
    def calculate_overtime_pay(base_salary: Decimal, overtime_hours: int) -> Decimal:
        if not overtime_hours:
            return Decimal('0')
        
        hourly_rate = base_salary / Decimal('160')
        return overtime_hours * hourly_rate * Decimal('1.5')


class VacationCalculator:
    @staticmethod
    def calculate_vacation_pay(base_salary: Decimal, vacation_days: int) -> Decimal:
        if not vacation_days:
            return Decimal('0')
        
        daily_rate = base_salary / Decimal('21')
        return vacation_days * daily_rate


class SalaryProcessor:
    def __init__(self):
        self.bonus_factory = BonusCalculatorFactory()
        self.tax_calculator = TaxCalculator()
        self.overtime_calculator = OvertimeCalculator()
        self.vacation_calculator = VacationCalculator()
    
    def _create_employee(self, data: Dict) -> Employee:
        """Создает объект Employee из словаря данных"""
        return Employee(
            id=data.get('id', 0),
            base_salary=Decimal(data.get('base_salary', 0)),
            department=data.get('department', '').lower(),
            position=data.get('position', '').lower(),
            years_of_experience=data.get('years_of_experience', 0),
            sales_amount=Decimal(data.get('sales_amount', 0)),
            overtime=data.get('overtime', 0),
            vacation_days=data.get('vacation_days', 0),
            team_size=data.get('team_size', 0)
        )
    
    def _calculate_salary(self, employee: Employee) -> SalaryCalculation:
        """Выполняет все расчеты для одного сотрудника"""
        # Расчет бонусов
        bonus_calculator = self.bonus_factory.get_calculator(employee.department)
        bonus = bonus_calculator.calculate_bonus(employee)
        
        # Расчет сверхурочных
        overtime_pay = self.overtime_calculator.calculate_overtime_pay(
            employee.base_salary, employee.overtime
        )
        
        # Расчет отпускных
        vacation_pay = self.vacation_calculator.calculate_vacation_pay(
            employee.base_salary, employee.vacation_days
        )
        
        # Расчет до вычетов
        total_before_tax = employee.base_salary + bonus + overtime_pay
        total_before_deductions = total_before_tax + vacation_pay
        
        # Расчет налогов и вычетов
        tax = self.tax_calculator.calculate_tax(total_before_tax)
        social_security = self.tax_calculator.calculate_social_security(total_before_tax)
        medicare = self.tax_calculator.calculate_medicare(total_before_tax)
        total_deductions = tax + social_security + medicare
        
        # Итоговая зарплата
        final_salary = total_before_deductions - total_deductions
        
        return SalaryCalculation(
            base_salary=employee.base_salary,
            bonus=bonus,
            overtime_pay=overtime_pay,
            vacation_pay=vacation_pay,
            total_before_deductions=total_before_deductions,
            tax=tax,
            social_security=social_security,
            medicare=medicare,
            total_deductions=total_deductions,
            final_salary=final_salary,
            calculation_date=datetime.now().strftime('%Y-%m-%d')
        )
    
    def calculate_payroll(self, employees_data: List[Dict]) -> Dict[int, Dict]:
        """Основной метод для расчета зарплат"""
        result = {}
        
        for emp_data in employees_data:
            try:
                employee = self._create_employee(emp_data)
                calculation = self._calculate_salary(employee)
                
                result[employee.id] = {
                    'base_salary': float(calculation.base_salary),
                    'bonus': float(calculation.bonus),
                    'overtime_pay': float(calculation.overtime_pay),
                    'vacation_pay': float(calculation.vacation_pay),
                    'total_before_deductions': float(calculation.total_before_deductions),
                    'tax': float(calculation.tax),
                    'social_security': float(calculation.social_security),
                    'medicare': float(calculation.medicare),
                    'total_deductions': float(calculation.total_deductions),
                    'final_salary': float(calculation.final_salary),
                    'calculation_date': calculation.calculation_date
                }
            
            except Exception as e:
                print(f"Error processing employee {emp_data.get('id')}: {str(e)}")
                continue
        
        return result


# Пример использования
if __name__ == "__main__":
    processor = SalaryProcessor()
    
    employees = [
        {
            'id': 1,
            'base_salary': 50000,
            'department': 'sales',
            'position': 'senior',
            'years_of_experience': 6,
            'sales_amount': 120000,
            'overtime': 10,
            'vacation_days': 5
        }
    ]
    
    result = processor.calculate_payroll(employees)
    print(result)