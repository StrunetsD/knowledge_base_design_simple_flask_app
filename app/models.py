from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric, Text, ForeignKey, CheckConstraint, Enum, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from sqlalchemy import event
from enum import Enum as PyEnum
import datetime

Base = declarative_base()


course_assignments = Table('course_assignments', Base.metadata,
    Column('assignment_id', Integer, ForeignKey('assignments.id')),
    Column('employee_id', Integer, ForeignKey('employees.id'))
)

class CourseType(PyEnum):
    IT = "информационные технологии"
    MANAGEMENT = "менеджмент"
    OTHER = "другое"

class TeacherCategory(PyEnum):
    HIGHEST = "высшая"
    FIRST = "первая"
    SECOND = "вторая"

class Organization(Base):
    __tablename__ = 'organizations'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    phone = Column(String(50))
    email = Column(String(100))
    
    courses = relationship("Course", back_populates="organization")

class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    type = Column(Enum(CourseType), nullable=False)
    duration_days = Column(Integer, nullable=False, default=1)
    max_students = Column(Integer, nullable=False, default=10)
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    
    organization = relationship("Organization", back_populates="courses")
    price_history = relationship("PriceHistory", back_populates="course")
    assignments = relationship("Assignment", back_populates="course")

class PriceHistory(Base):
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    document_number = Column(String(100), nullable=False)
    document_date = Column(Date, nullable=False, default=func.current_date())
    price = Column(Numeric(10, 2), nullable=False)
    valid_from = Column(Date, nullable=False, default=func.current_date())
    valid_to = Column(Date)
    
    course = relationship("Course", back_populates="price_history")
    
    __table_args__ = (
        CheckConstraint('price >= 0', name='check_price_positive'),
        CheckConstraint('valid_to IS NULL OR valid_to > valid_from', name='check_valid_dates'),
    )
    
    @property
    def price_with_vat(self):
        return self.price * 1.2 

class Teacher(Base):
    __tablename__ = 'teachers'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(Enum('M', 'F', name='gender_types'))
    education = Column(Text)
    category = Column(Enum(TeacherCategory))
    
    assignments = relationship("Assignment", back_populates="teacher")

class Assignment(Base):
    __tablename__ = 'assignments'
    
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    document_number = Column(String(100), nullable=False)
    document_date = Column(Date, nullable=False, default=func.current_date())

    teacher = relationship("Teacher", back_populates="assignments")
    course = relationship("Course", back_populates="assignments")
    
    __table_args__ = (
        CheckConstraint('end_date > start_date', name='check_dates_order'),
    )
    
    def is_weekend(self, date):
        return date.weekday() >= 5  # 5=Saturday, 6=Sunday
    
    def validate_dates(self):
        current_date = self.start_date
        while current_date <= self.end_date:
            if self.is_weekend(current_date):
                raise ValueError("Обучение не может проводиться в выходные дни")
            current_date += datetime.timedelta(days=1)

class ClientOrganization(Base):
    __tablename__ = 'client_organizations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    phone = Column(String(50))
    email = Column(String(100))
    
    training_requests = relationship("TrainingRequest", back_populates="client_organization")

class TrainingRequest(Base):
    __tablename__ = 'training_requests'
    
    id = Column(Integer, primary_key=True)
    client_organization_id = Column(Integer, ForeignKey('client_organizations.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    required_start_date = Column(Date, nullable=False)
    required_end_date = Column(Date, nullable=False)
    number_of_people = Column(Integer, nullable=False, default=1)
    
    client_organization = relationship("ClientOrganization", back_populates="training_requests")
    course = relationship("Course")
    employees = relationship("Employee", back_populates="training_request")
    
    __table_args__ = (
        CheckConstraint('required_end_date > required_start_date', name='check_training_dates_order'),
        CheckConstraint('number_of_people > 0', name='check_positive_people'),
    )

class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True)
    training_request_id = Column(Integer, ForeignKey('training_requests.id'))
    full_name = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    
    training_request = relationship("TrainingRequest", back_populates="employees")
    assignments = relationship("Assignment", secondary=course_assignments, backref="employees")

@event.listens_for(Assignment, 'before_insert')
@event.listens_for(Assignment, 'before_update')
def validate_assignment_dates(mapper, connection, target):
    target.validate_dates()