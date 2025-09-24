from sqlalchemy import Column, Integer, String, Date, Float, Enum, Boolean, ForeignKey, Table, event, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
import enum
from datetime import datetime

Base = declarative_base()


course_instructor_association = Table(
    'course_instructor_association',
    Base.metadata,
    Column('course_id', Integer, ForeignKey('courses.id', ondelete='CASCADE'), primary_key=True),
    Column('instructor_id', Integer, ForeignKey('instructors.id', ondelete='CASCADE'), primary_key=True),
    Column('assignment_document_id', Integer, ForeignKey('assignment_documents.id', ondelete='CASCADE'))
)

class Organization(Base):
    __tablename__ = 'organizations'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    address = Column(String(300), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    
    courses = relationship("Course", back_populates="organization")
    training_requests = relationship("TrainingRequest", back_populates="client_organization")

class CourseType(enum.Enum):
    IT = "информационные технологии"
    MANAGEMENT = "менеджмент"
    OTHER = "другое"
    MARKETING = "маркетинг"
    DESIGN = "дизайн"

class InstructorCategory(enum.Enum):
    HIGHEST = "высшая"
    FIRST = "первая"
    SECOND = "вторая"

class Instructor(Base):
    __tablename__ = 'instructors'
    
    id = Column(Integer, primary_key=True)
    number = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    education = Column(String(200), nullable=False)
    category = Column(Enum(InstructorCategory), nullable=False)
    
    courses = relationship("Course", 
                          secondary=course_instructor_association, 
                          back_populates="instructors",
                          overlaps="assigned_courses")
    assignment_documents = relationship("AssignmentDocument", back_populates="instructor")

class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    course_type = Column(Enum(CourseType), nullable=False)
    duration_days = Column(Integer, nullable=False)
    max_students = Column(Integer, nullable=False)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    organization = relationship("Organization", back_populates="courses")
    instructors = relationship("Instructor", 
                              secondary=course_instructor_association, 
                              back_populates="courses",
                              overlaps="assigned_courses")
    prices = relationship("CoursePrice", back_populates="course")
    training_requests = relationship("TrainingRequest", back_populates="course")
    assignment_documents = relationship("AssignmentDocument", back_populates="course")

class CoursePrice(Base):
    __tablename__ = 'course_prices'
    
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    price = Column(Float, nullable=False)
    price_with_vat = Column(Float, nullable=False)  
    document_number = Column(String(100), nullable=False)
    document_date = Column(Date, nullable=False)
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date, nullable=True) 
    
    course = relationship("Course", back_populates="prices")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._calculate_vat()
    
    def _calculate_vat(self):
        if self.price is not None:
            self.price_with_vat = self.price * 1.2
    
    @validates('price')
    def validate_price(self, key, price):
        if price is not None and price <= 0:
            raise ValueError("Цена должна быть положительной")
        return price  

class AssignmentDocument(Base):
    __tablename__ = 'assignment_documents'
    
    id = Column(Integer, primary_key=True)
    document_number = Column(String(100), nullable=False)
    document_date = Column(Date, nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    instructor_id = Column(Integer, ForeignKey('instructors.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    course = relationship("Course", back_populates="assignment_documents")
    instructor = relationship("Instructor", back_populates="assignment_documents")
    
    __table_args__ = (
        CheckConstraint(
            "EXTRACT(DOW FROM start_date) NOT IN (0, 6)",
            name='check_start_date_not_weekend'
        ),
        CheckConstraint(
            "EXTRACT(DOW FROM end_date) NOT IN (0, 6)", 
            name='check_end_date_not_weekend'
        ),
        CheckConstraint(
            "end_date >= start_date",
            name='check_end_date_after_start'
        ),
    )
    
    @validates('start_date', 'end_date')
    def validate_dates(self, key, date):
        if date.weekday() in [5, 6]: 
            raise ValueError(f"{key} cannot be on weekend (Saturday or Sunday)")
        
        if key == 'end_date' and hasattr(self, 'start_date') and self.start_date and date < self.start_date:
            raise ValueError("End date must be after start date")
        if key == 'start_date' and hasattr(self, 'end_date') and self.end_date and date > self.end_date:
            raise ValueError("Start date must be before end date")
        
        return date

class TrainingRequest(Base):
    __tablename__ = 'training_requests'
    
    id = Column(Integer, primary_key=True)
    client_organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    requested_start_date = Column(Date, nullable=False)
    requested_end_date = Column(Date, nullable=False)
    number_of_students = Column(Integer, nullable=False)
    contact_phone = Column(String(20))
    contact_email = Column(String(100))
    created_date = Column(Date, default=func.current_date())
    
    client_organization = relationship("Organization", back_populates="training_requests")
    course = relationship("Course", back_populates="training_requests")
    students = relationship("Student", back_populates="training_request")
    
    __table_args__ = (
        CheckConstraint(
            "EXTRACT(DOW FROM requested_start_date) NOT IN (0, 6)",
            name='check_requested_start_date_not_weekend'
        ),
        CheckConstraint(
            "EXTRACT(DOW FROM requested_end_date) NOT IN (0, 6)",
            name='check_requested_end_date_not_weekend'
        ),
        CheckConstraint(
            "requested_end_date >= requested_start_date",
            name='check_requested_end_date_after_start'
        ),
    )
    
    @validates('requested_start_date', 'requested_end_date')
    def validate_dates(self, key, date):
        if date.weekday() in [5, 6]: 
            raise ValueError(f"{key} cannot be on weekend (Saturday or Sunday)")
        
        if key == 'requested_end_date' and hasattr(self, 'requested_start_date') and self.requested_start_date and date < self.requested_start_date:
            raise ValueError("Requested end date must be after requested start date")
        if key == 'requested_start_date' and hasattr(self, 'requested_end_date') and self.requested_end_date and date > self.requested_end_date:
            raise ValueError("Requested start date must be before requested end date")
        
        return date

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    training_request_id = Column(Integer, ForeignKey('training_requests.id'), nullable=False)
    full_name = Column(String(200), nullable=False)
    position = Column(String(200), nullable=False)
    
    training_request = relationship("TrainingRequest", back_populates="students")


@event.listens_for(CoursePrice, 'before_insert')
@event.listens_for(CoursePrice, 'before_update')
def calculate_price_with_vat(mapper, connection, target):
    if target.price is not None:
        target.price_with_vat = target.price * 1.2


@event.listens_for(AssignmentDocument, 'before_insert')
@event.listens_for(AssignmentDocument, 'before_update')
def validate_assignment_dates(mapper, connection, target):
    if target.start_date and target.start_date.weekday() in [5, 6]:
        raise ValueError("Start date cannot be on weekend")
    if target.end_date and target.end_date.weekday() in [5, 6]:
        raise ValueError("End date cannot be on weekend")
    if target.start_date and target.end_date and target.end_date < target.start_date:
        raise ValueError("End date must be after start date")

@event.listens_for(TrainingRequest, 'before_insert')
@event.listens_for(TrainingRequest, 'before_update')
def validate_training_dates(mapper, connection, target):
    if target.requested_start_date and target.requested_start_date.weekday() in [5, 6]:
        raise ValueError("Requested start date cannot be on weekend")
    if target.requested_end_date and target.requested_end_date.weekday() in [5, 6]:
        raise ValueError("Requested end date cannot be on weekend")
    if (target.requested_start_date and target.requested_end_date and 
        target.requested_end_date < target.requested_start_date):
        raise ValueError("Requested end date must be after requested start date")
    