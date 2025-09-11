from models import *
from db_conn import get_session

def add_organization(code, name, address, phone=None, email=None):
    with get_session() as session:
        new_org = Organization(
            code=code,
            name=name,
            address=address,
            phone=phone,
            email=email
        )
        session.add(new_org)
        return new_org

def update_organization(org_id, **kwargs):
    with get_session() as session:
        org = session.query(Organization).filter(Organization.id == org_id).first()
        if org:
            for key, value in kwargs.items():
                if hasattr(org, key):
                    setattr(org, key, value)
            return org
        return None

def delete_organization(org_id):
    with get_session() as session:
        org = session.query(Organization).filter(Organization.id == org_id).first()
        if org:
            session.delete(org)
            return True
        return False

def get_all_organizations():
    with get_session() as session:
        return session.query(Organization).all()

def add_course(code, title, type, duration_days, max_students, organization_id):
    with get_session() as session:
        new_course = Course(
            code=code,
            title=title,
            type=type,
            duration_days=duration_days,
            max_students=max_students,
            organization_id=organization_id
        )
        session.add(new_course)
        return new_course

def update_course(course_id, **kwargs):
    with get_session() as session:
        course = session.query(Course).filter(Course.id == course_id).first()
        if course:
            for key, value in kwargs.items():
                if hasattr(course, key):
                    setattr(course, key, value)
            return course
        return None

def delete_course(course_id):
    with get_session() as session:
        course = session.query(Course).filter(Course.id == course_id).first()
        if course:
            session.delete(course)
            return True
        return False

def get_all_courses():
    with get_session() as session:
        return session.query(Course).all()

def get_courses_by_organization(org_id):
    with get_session() as session:
        return session.query(Course).filter(Course.organization_id == org_id).all()

def add_price_history(course_id, document_number, price, valid_from, valid_to=None):
    with get_session() as session:
        price_history = PriceHistory(
            course_id=course_id,
            document_number=document_number,
            price=price,
            valid_from=valid_from,
            valid_to=valid_to
        )
        session.add(price_history)
        return price_history

def get_current_course_price(course_id):
    with get_session() as session:
        current_price = session.query(PriceHistory).filter(
            PriceHistory.course_id == course_id,
            PriceHistory.valid_from <= date.today(),
            (PriceHistory.valid_to == None) | (PriceHistory.valid_to >= date.today())
        ).order_by(PriceHistory.valid_from.desc()).first()
        return current_price

def get_course_price_history(course_id):
    with get_session() as session:
        return session.query(PriceHistory).filter(
            PriceHistory.course_id == course_id
        ).order_by(PriceHistory.valid_from.desc()).all()

def add_teacher(code, full_name, birth_date, gender, education=None, category=None):
    with get_session() as session:
        new_teacher = Teacher(
            code=code,
            full_name=full_name,
            birth_date=birth_date,
            gender=gender,
            education=education,
            category=category
        )
        session.add(new_teacher)
        return new_teacher

def update_teacher(teacher_id, **kwargs):
    with get_session() as session:
        teacher = session.query(Teacher).filter(Teacher.id == teacher_id).first()
        if teacher:
            for key, value in kwargs.items():
                if hasattr(teacher, key):
                    setattr(teacher, key, value)
            return teacher
        return None

def delete_teacher(teacher_id):
    with get_session() as session:
        teacher = session.query(Teacher).filter(Teacher.id == teacher_id).first()
        if teacher:
            session.delete(teacher)
            return True
        return False

def get_all_teachers():
    with get_session() as session:
        return session.query(Teacher).all()

def add_assignment(teacher_id, course_id, document_number, document_date, start_date, end_date):
    with get_session() as session:
        assignment = Assignment(
            teacher_id=teacher_id,
            course_id=course_id,
            document_number=document_number,
            document_date=document_date,
            start_date=start_date,
            end_date=end_date
        )
        assignment.validate_dates()  
        session.add(assignment)
        return assignment

def update_assignment(assignment_id, **kwargs):
    with get_session() as session:
        assignment = session.query(Assignment).filter(Assignment.id == assignment_id).first()
        if assignment:
            for key, value in kwargs.items():
                if hasattr(assignment, key):
                    setattr(assignment, key, value)
            assignment.validate_dates()  
            return assignment
        return None

def delete_assignment(assignment_id):
    with get_session() as session:
        assignment = session.query(Assignment).filter(Assignment.id == assignment_id).first()
        if assignment:
            session.delete(assignment)
            return True
        return False

def add_client_organization(name, address, phone=None, email=None):
    with get_session() as session:
        new_client_org = ClientOrganization(
            name=name,
            address=address,
            phone=phone,
            email=email
        )
        session.add(new_client_org)
        return new_client_org

def add_training_request(client_organization_id, course_id, required_start_date, 
                        required_end_date, number_of_people):
    with get_session() as session:
        training_request = TrainingRequest(
            client_organization_id=client_organization_id,
            course_id=course_id,
            required_start_date=required_start_date,
            required_end_date=required_end_date,
            number_of_people=number_of_people
        )
        session.add(training_request)
        return training_request

def update_training_request(request_id, **kwargs):
    with get_session() as session:
        request = session.query(TrainingRequest).filter(TrainingRequest.id == request_id).first()
        if request:
            for key, value in kwargs.items():
                if hasattr(request, key):
                    setattr(request, key, value)
            return request
        return None

def delete_training_request(request_id):
    with get_session() as session:
        request = session.query(TrainingRequest).filter(TrainingRequest.id == request_id).first()
        if request:
            session.delete(request)
            return True
        return False

def add_employee(training_request_id, full_name, position):
    with get_session() as session:
        employee = Employee(
            training_request_id=training_request_id,
            full_name=full_name,
            position=position
        )
        session.add(employee)
        return employee

def get_all_training_requests():
    with get_session() as session:
        return session.query(TrainingRequest).all()

def get_training_requests_by_client(client_org_id):
    with get_session() as session:
        return session.query(TrainingRequest).filter(
            TrainingRequest.client_organization_id == client_org_id
        ).all()

def get_employees_by_request(request_id):
    with get_session() as session:
        return session.query(Employee).filter(
            Employee.training_request_id == request_id
        ).all()

def get_assignments_by_teacher(teacher_id):
    with get_session() as session:
        return session.query(Assignment).filter(
            Assignment.teacher_id == teacher_id
        ).all()

def get_assignments_by_course(course_id):
    with get_session() as session:
        return session.query(Assignment).filter(
            Assignment.course_id == course_id
        ).all()
    
def get_organization_price_list(organization_id, target_date=None):

    if target_date is None:
        target_date = date.today()
    
    with get_session() as session:
        latest_prices = session.query(
            PriceHistory.course_id,
            func.max(PriceHistory.valid_from).label('max_valid_from')
        ).filter(
            PriceHistory.valid_from <= target_date,
            or_(PriceHistory.valid_to == None, PriceHistory.valid_to >= target_date)
        ).group_by(PriceHistory.course_id).subquery()
        
        price_list = session.query(
            Course.code,
            Course.title,
            Course.type,
            Course.duration_days,
            Course.max_students,
            PriceHistory.price,
            PriceHistory.price_with_vat,
            PriceHistory.document_number,
            PriceHistory.document_date,
            PriceHistory.valid_from,
            PriceHistory.valid_to
        ).join(PriceHistory, Course.id == PriceHistory.course_id
        ).join(latest_prices, and_(
            PriceHistory.course_id == latest_prices.c.course_id,
            PriceHistory.valid_from == latest_prices.c.max_valid_from
        )).filter(
            Course.organization_id == organization_id
        ).order_by(Course.title).all()
        
        return price_list

def get_all_client_organizations():
    with get_session() as session:
        return session.query(ClientOrganization).all()
    
def get_all_organizations_price_list(target_date=None):

    if target_date is None:
        target_date = date.today()
    
    with get_session() as session:
        latest_prices = session.query(
            PriceHistory.course_id,
            func.max(PriceHistory.valid_from).label('max_valid_from')
        ).filter(
            PriceHistory.valid_from <= target_date,
            or_(PriceHistory.valid_to == None, PriceHistory.valid_to >= target_date)
        ).group_by(PriceHistory.course_id).subquery()
        
        price_list = session.query(
            Organization.name.label('organization_name'),
            Course.code,
            Course.title,
            Course.type,
            Course.duration_days,
            PriceHistory.price,
            PriceHistory.price_with_vat,
            PriceHistory.document_number,
            PriceHistory.document_date
        ).join(Course, Organization.id == Course.organization_id
        ).join(PriceHistory, Course.id == PriceHistory.course_id
        ).join(latest_prices, and_(
            PriceHistory.course_id == latest_prices.c.course_id,
            PriceHistory.valid_from == latest_prices.c.max_valid_from
        )).order_by(Organization.name, Course.title).all()
        
        return price_list

def get_course_price_changes(course_id):

    with get_session() as session:
        price_changes = session.query(
            PriceHistory.document_number,
            PriceHistory.document_date,
            PriceHistory.price,
            PriceHistory.price_with_vat,
            PriceHistory.valid_from,
            PriceHistory.valid_to
        ).filter(
            PriceHistory.course_id == course_id
        ).order_by(PriceHistory.valid_from.desc()).all()
        
        return price_changes
    
def get_teacher_schedule(teacher_id, start_date, end_date):

    with get_session() as session:
        schedule = session.query(
            Assignment.id,
            Course.title.label('course_title'),
            Course.code.label('course_code'),
            Course.duration_days,
            Assignment.start_date,
            Assignment.end_date,
            Assignment.document_number,
            Assignment.document_date
        ).join(Course, Assignment.course_id == Course.id
        ).filter(
            Assignment.teacher_id == teacher_id,
            Assignment.start_date <= end_date,
            Assignment.end_date >= start_date
        ).order_by(Assignment.start_date).all()
        
        return schedule


def get_course_group_fill(course_id, start_date, end_date):

    with get_session() as session:
        course = session.query(Course.max_students).filter(Course.id == course_id).first()
        max_students = course.max_students if course else 0
        
        assignments = session.query(
            Assignment.id,
            Assignment.start_date,
            Assignment.end_date,
            func.count(course_assignments.c.employee_id).label('current_students'),
            case(
                (func.count(course_assignments.c.employee_id) >= max_students, 'Полностью набрана'),
                (func.count(course_assignments.c.employee_id) == 0, 'Пустая'),
                else_='Частично набрана'
            ).label('fill_status')
        ).outerjoin(course_assignments, Assignment.id == course_assignments.c.assignment_id
        ).filter(
            Assignment.course_id == course_id,
            Assignment.start_date <= end_date,
            Assignment.end_date >= start_date
        ).group_by(Assignment.id).order_by(Assignment.start_date).all()
        
        result = []
        for assignment in assignments:
            result.append({
                'assignment_id': assignment.id,
                'start_date': assignment.start_date,
                'end_date': assignment.end_date,
                'current_students': assignment.current_students,
                'max_students': max_students,
                'fill_percentage': (assignment.current_students / max_students * 100) if max_students > 0 else 0,
                'fill_status': assignment.fill_status,
                'is_full': assignment.current_students >= max_students
            })
        
        return result

def get_group_students(assignment_id):

    with get_session() as session:
        students = session.query(
            Employee.id,
            Employee.full_name,
            Employee.position,
            TrainingRequest.id.label('request_id'),
            ClientOrganization.name.label('client_organization')
        ).join(course_assignments, Employee.id == course_assignments.c.employee_id
        ).join(TrainingRequest, Employee.training_request_id == TrainingRequest.id
        ).join(ClientOrganization, TrainingRequest.client_organization_id == ClientOrganization.id
        ).filter(
            course_assignments.c.assignment_id == assignment_id
        ).order_by(Employee.full_name).all()
        
        return students


def get_course_available_slots(course_id, start_date, end_date):

    with get_session() as session:
        course = session.query(Course.max_students).filter(Course.id == course_id).first()
        max_students = course.max_students if course else 0
        
        available_slots = session.query(
            Assignment.id,
            Assignment.start_date,
            Assignment.end_date,
            (max_students - func.count(course_assignments.c.employee_id)).label('available_slots'),
            func.count(course_assignments.c.employee_id).label('current_students'),
            max_students.label('max_students')
        ).outerjoin(course_assignments, Assignment.id == course_assignments.c.assignment_id
        ).filter(
            Assignment.course_id == course_id,
            Assignment.start_date <= end_date,
            Assignment.end_date >= start_date
        ).group_by(Assignment.id).order_by(Assignment.start_date).all()
        
        return available_slots

def find_available_course_groups(course_id, required_start_date=None, required_end_date=None):

    if required_start_date is None:
        required_start_date = date.today()
    if required_end_date is None:
        required_end_date = required_start_date + timedelta(days=30)
    
    with get_session() as session:
        course = session.query(Course.max_students).filter(Course.id == course_id).first()
        max_students = course.max_students if course else 0
        
        groups = session.query(
            Assignment.id,
            Assignment.start_date,
            Assignment.end_date,
            (max_students - func.count(course_assignments.c.employee_id)).label('available_slots'),
            func.count(course_assignments.c.employee_id).label('current_students')
        ).outerjoin(course_assignments, Assignment.id == course_assignments.c.assignment_id
        ).filter(
            Assignment.course_id == course_id,
            Assignment.start_date >= required_start_date,
            Assignment.end_date <= required_end_date,
            (max_students - func.count(course_assignments.c.employee_id)) > 0
        ).group_by(Assignment.id).order_by(Assignment.start_date).all()
        
        return groups