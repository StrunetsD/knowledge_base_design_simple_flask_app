from models import *
from db_conn import get_session
from sqlalchemy import func, and_, or_
from datetime import date
from decimal import Decimal


def add_organization(session, code, name, address, phone=None, email=None):
    existing_org = session.query(Organization).filter_by(code=code).first()
    
    if existing_org:
        print(f"Организация с кодом {code} уже существует.")
        return existing_org  
    
    org = Organization(
        code=code,
        name=name,
        address=address,
        phone=phone,
        email=email
    )
    session.add(org)
    session.commit()
    return org

def update_organization(session, org_id, **kwargs):

    org = session.get(Organization, org_id)
    if org:
        for key, value in kwargs.items():
            if hasattr(org, key):
                setattr(org, key, value)
        session.commit()
    return org

def assign_instructor_to_course(session, instructor_id, course_id):
    instructor = session.get(Instructor, instructor_id)
    course = session.get(Course, course_id)
    
    if instructor and course:
        if course not in instructor.courses:
            instructor.courses.append(course)
            session.commit()
            return True
    return False

def remove_instructor_from_course(session, instructor_id, course_id):
    instructor = session.get(Instructor, instructor_id)
    course = session.get(Course, course_id)
    
    if instructor and course:
        if course in instructor.courses:
            instructor.courses.remove(course)
            session.commit()
            return True
    return False

def get_course_instructors(session, course_id):
    course = session.get(Course, course_id)
    return course.instructors if course else []

def get_instructor_courses(session, instructor_id):
    instructor = session.get(Instructor, instructor_id)
    return instructor.courses if instructor else []

def delete_organization(session, org_id):
    org = session.get(Organization, org_id)
    
    if org:
        courses = session.query(Course).filter(Course.organization_id == org_id).all()
        
        for course in courses:
            instructor_associations = session.query(CourseInstructorAssociation).filter(
                CourseInstructorAssociation.course_id == course.id
            ).all()
            
            for association in instructor_associations:
                session.delete(association)
            
            assignments = session.query(AssignmentDocument).filter(
                AssignmentDocument.course_id == course.id
            ).all()
            
            for assignment in assignments:
                session.delete(assignment)
            
            prices = session.query(CoursePrice).filter(
                CoursePrice.course_id == course.id
            ).all()
            
            for price in prices:
                session.delete(price)
            
            session.delete(course)
        
        session.delete(org)
        session.commit()
        return True
    
    return False
  

def add_course(session, code, name, course_type_str, duration_days, max_students, organization_id):
    type_mapping = {
        "информационные технологии": CourseType.IT,
        "управление": CourseType.MANAGEMENT,
        "маркетинг": CourseType.MARKETING,
        "дизайн": CourseType.DESIGN
    }
    
    try:
        course_type = type_mapping[course_type_str.lower()]
    except KeyError:
        raise ValueError(f"Invalid course type: {course_type_str}")

    existing_course = session.query(Course).filter_by(code=code).first()
    if existing_course:
        print(f"Курс с кодом {code} уже существует.")
        return existing_course  
    
    course = Course(
        code=code,
        name=name,
        course_type=course_type,  
        duration_days=duration_days,
        max_students=max_students,
        organization_id=organization_id
    )
    session.add(course)
    session.commit()
    return course

def update_course(session, course_id, **kwargs):
    course = session.get(Course, course_id)
    if course:
        for key, value in kwargs.items():
            if hasattr(course, key):
                setattr(course, key, value)
        session.commit()
    return course

def delete_course(session, course_id):
    course = session.get(Course, course_id)
    if course:
        session.query(Student).filter(
            Student.training_request_id.in_(
                session.query(TrainingRequest.id).filter(TrainingRequest.course_id == course_id)
            )
        ).delete(synchronize_session=False)
        
        session.query(TrainingRequest).filter(TrainingRequest.course_id == course_id).delete()
        
        session.query(CoursePrice).filter(CoursePrice.course_id == course_id).delete()
        
        session.query(AssignmentDocument).filter(AssignmentDocument.course_id == course_id).delete()
        
        session.delete(course)
        session.commit()
        return True
    return False

def add_course_price(session, course_id, price, document_number, document_date, valid_from, valid_to=None):
    price_obj = CoursePrice(
        course_id=course_id,
        price=price,
        document_number=document_number,
        document_date=document_date,
        valid_from=valid_from,
        valid_to=valid_to
    )
    session.add(price_obj)
    session.commit()
    return price_obj

def add_instructor(session, number, full_name, birth_date, gender_str, education, category_str):
    gender_mapping = {
        "М": "М",  
        "Ж": "Ж",
    }
    
    category_mapping = {
        "высшая": InstructorCategory.HIGHEST,
        "первая": InstructorCategory.FIRST,
        "вторая": InstructorCategory.SECOND
    }
    
    try:
        gender = gender_mapping[gender_str]
    except KeyError:
        raise ValueError(f"Invalid gender: {gender_str}")
    
    try:
        category = category_mapping[category_str]
    except KeyError:
        raise ValueError(f"Invalid category: {category_str}")

    existing_instructor = session.query(Instructor).filter_by(number=number).first()

    if existing_instructor:
        print(f"Преподаватель с номером {number} уже существует.")
        return existing_instructor
    
    instructor = Instructor(
        number=number,
        full_name=full_name,
        birth_date=birth_date,
        gender=gender,
        education=education,
        category=category
    )
    
    try:
        session.add(instructor)
        session.commit()
        return instructor
    except Exception as e:
        session.rollback()
        raise e

def update_instructor(session, instructor_id, **kwargs):
    instructor = session.get(Instructor, instructor_id)
    if instructor:
        category_mapping = {
            "высшая": InstructorCategory.HIGHEST,
            "первая": InstructorCategory.FIRST,
            "вторая": InstructorCategory.SECOND
        }
        
        for key, value in kwargs.items():
            if key == 'category' and value in category_mapping:
                setattr(instructor, key, category_mapping[value])
            elif hasattr(instructor, key):
                setattr(instructor, key, value)
        session.commit()
    return instructor

def delete_instructor(session, instructor_id):
    instructor = session.get(Instructor, instructor_id)
    if instructor:
        session.delete(instructor)
        session.commit()
        return True
    return False

def add_training_request(session, client_organization_id, course_id, requested_start_date, 
                        requested_end_date, number_of_students, contact_phone, contact_email):
    request = TrainingRequest(
        client_organization_id=client_organization_id,
        course_id=course_id,
        requested_start_date=requested_start_date,
        requested_end_date=requested_end_date,
        number_of_students=number_of_students,
        contact_phone=contact_phone,
        contact_email=contact_email
    )
    session.add(request)
    session.commit()
    return request

def update_training_request(session, request_id, **kwargs):
    request = session.get(TrainingRequest, request_id)
    if request:
        for key, value in kwargs.items():
            if hasattr(request, key):
                setattr(request, key, value)
        session.commit()
    return request

def get_price_list(session, organization_id, target_date):
    results = session.query(
        Course.name,
        Course.duration_days,
        CoursePrice.price,
        (CoursePrice.price * Decimal('1.2')).label('price_with_vat')
    ).select_from(Course).join(CoursePrice).filter(
        Course.organization_id == organization_id,
        CoursePrice.valid_from <= target_date,
        or_(
            CoursePrice.valid_to >= target_date,
            CoursePrice.valid_to.is_(None)
        )
    ).distinct().all()  
    
    return results

def get_instructor_schedule(session, instructor_id, start_date, end_date):
    results = session.query(
        Course.name,
        AssignmentDocument.start_date,
        AssignmentDocument.end_date
    ).join(Course).filter(
        AssignmentDocument.instructor_id == instructor_id,
        AssignmentDocument.start_date >= start_date,
        AssignmentDocument.end_date <= end_date
    ).all()
    
    return results

def get_course_groups_fill(session, course_id, start_date, end_date):
    requests = session.query(TrainingRequest).filter(
        TrainingRequest.course_id == course_id,
        TrainingRequest.requested_start_date >= start_date,
        TrainingRequest.requested_end_date <= end_date
    ).all()
    
    result = []
    for req in requests:
        student_count = session.query(func.count(Student.id)).filter(
            Student.training_request_id == req.id
        ).scalar()
        
        course = session.get(Course, course_id)
        
        result.append({
            'request_id': req.id,
            'start_date': req.requested_start_date,
            'end_date': req.requested_end_date,
            'student_count': student_count,
            'max_students': course.max_students,
            'is_full': student_count >= course.max_students
        })
    
    return result

def add_assignment_document(session, document_number, document_date, instructor_id, course_ids, start_date, end_date):
    doc = AssignmentDocument(
        document_number=document_number,
        document_date=document_date,
        instructor_id=instructor_id,
        start_date=start_date,
        end_date=end_date
    )
    
    for course_id in course_ids:
        course = session.get(Course, course_id)
        if course:
            doc.course_id = course.id  
    
    session.add(doc)
    session.commit()
    return doc

def add_student(session, training_request_id, full_name, position):
    student = Student(
        training_request_id=training_request_id,
        full_name=full_name,
        position=position
    )
    session.add(student)
    session.commit()
    return student
