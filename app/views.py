# app/views.py
from flask import Blueprint, jsonify, request
from datetime import datetime
from functools import wraps
import logging
from models import *
from db_requests import *

api = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    return decorated_function

def parse_date(date_str):
    if not date_str:
        return None
    return datetime.strptime(date_str, '%Y-%m-%d').date()

@api.route('/organizations', methods=['GET'])
@handle_errors
def get_organizations():
    organizations = get_all_organizations()
    return jsonify({
        'success': True,
        'data': [{
            'id': org.id,
            'code': org.code,
            'name': org.name,
            'address': org.address,
            'phone': org.phone,
            'email': org.email
        } for org in organizations]
    })

@api.route('/organizations', methods=['POST'])
@handle_errors
def create_organization():
    data = request.get_json()
    org = add_organization(
        code=data['code'],
        name=data['name'],
        address=data['address'],
        phone=data.get('phone'),
        email=data.get('email')
    )
    return jsonify({
        'success': True,
        'message': 'Organization created successfully',
        'data': {'id': org.id}
    }), 201


@api.route('/courses', methods=['GET'])
@handle_errors
def get_courses():
    courses = get_all_courses()
    return jsonify({
        'success': True,
        'data': [{
            'id': course.id,
            'code': course.code,
            'title': course.title,
            'type': course.type.value,
            'type_display': course.type.name,
            'duration_days': course.duration_days,
            'max_students': course.max_students,
            'organization_id': course.organization_id
        } for course in courses]
    })

@api.route('/organizations/<int:org_id>/courses', methods=['GET'])
@handle_errors
def get_organization_courses(org_id):
    courses = get_courses_by_organization(org_id)
    return jsonify({
        'success': True,
        'data': [{
            'id': course.id,
            'code': course.code,
            'title': course.title,
            'type': course.type.value,
            'duration_days': course.duration_days,
            'max_students': course.max_students
        } for course in courses]
    })


@api.route('/organizations/<int:org_id>/price-list', methods=['GET'])
@handle_errors
def get_org_price_list(org_id):
    target_date = parse_date(request.args.get('date'))
    
    price_list = get_organization_price_list(org_id, target_date)
    return jsonify({
        'success': True,
        'data': [{
            'course_code': item.code,
            'course_title': item.title,
            'course_type': item.type.value,
            'duration_days': item.duration_days,
            'price': float(item.price),
            'price_with_vat': float(item.price_with_vat),
            'document_number': item.document_number,
            'valid_from': item.valid_from.isoformat(),
            'valid_to': item.valid_to.isoformat() if item.valid_to else None
        } for item in price_list]
    })


@api.route('/teachers', methods=['GET'])
@handle_errors
def get_teachers():
    teachers = get_all_teachers()
    return jsonify({
        'success': True,
        'data': [{
            'id': teacher.id,
            'code': teacher.code,
            'full_name': teacher.full_name,
            'birth_date': teacher.birth_date.isoformat(),
            'gender': teacher.gender,
            'education': teacher.education,
            'category': teacher.category.value if teacher.category else None,
            'category_display': teacher.category.name if teacher.category else None
        } for teacher in teachers]
    })

@api.route('/teachers', methods=['POST'])
@handle_errors
def create_teacher():
    data = request.get_json()
    teacher = add_teacher(
        code=data['code'],
        full_name=data['full_name'],
        birth_date=parse_date(data['birth_date']),
        gender=data['gender'],
        education=data.get('education'),
        category=TeacherCategory(data['category']) if data.get('category') else None
    )
    return jsonify({
        'success': True,
        'message': 'Teacher created successfully',
        'data': {'id': teacher.id}
    }), 201


@api.route('/teachers/<int:teacher_id>/schedule', methods=['GET'])
@handle_errors
def get_teacher_schedule_route(teacher_id):
    start_date = parse_date(request.args.get('start_date'))
    end_date = parse_date(request.args.get('end_date'))
    
    if not start_date or not end_date:
        return jsonify({'error': 'start_date and end_date are required'}), 400
    
    schedule = get_teacher_schedule(teacher_id, start_date, end_date)
    return jsonify({
        'success': True,
        'data': [{
            'id': item.id,
            'course_title': item.course_title,
            'course_code': item.course_code,
            'duration_days': item.duration_days,
            'start_date': item.start_date.isoformat(),
            'end_date': item.end_date.isoformat(),
            'document_number': item.document_number
        } for item in schedule]
    })


@api.route('/courses/<int:course_id>/groups', methods=['GET'])
@handle_errors
def get_course_groups(course_id):
    start_date = parse_date(request.args.get('start_date'))
    end_date = parse_date(request.args.get('end_date'))
    
    if not start_date or not end_date:
        return jsonify({'error': 'start_date and end_date are required'}), 400
    
    groups = get_course_group_fill(course_id, start_date, end_date)
    return jsonify({
        'success': True,
        'data': groups
    })

@api.route('/groups/<int:assignment_id>/students', methods=['GET'])
@handle_errors
def get_group_students_route(assignment_id):
    students = get_group_students(assignment_id)
    return jsonify({
        'success': True,
        'data': [{
            'id': student.id,
            'full_name': student.full_name,
            'position': student.position,
            'client_organization': student.client_organization
        } for student in students]
    })


@api.route('/courses/<int:course_id>/available-groups', methods=['GET'])
@handle_errors
def get_available_groups(course_id):
    start_date = parse_date(request.args.get('start_date'))
    end_date = parse_date(request.args.get('end_date'))
    
    groups = find_available_course_groups(course_id, start_date, end_date)
    return jsonify({
        'success': True,
        'data': [{
            'id': group.id,
            'start_date': group.start_date.isoformat(),
            'end_date': group.end_date.isoformat(),
            'available_slots': group.available_slots,
            'current_students': group.current_students
        } for group in groups]
    })


@api.route('/client-organizations', methods=['GET'])
@handle_errors
def get_client_organizations():
    with get_session() as session:
        orgs = session.query(ClientOrganization).all()
        return jsonify({
            'success': True,
            'data': [{
                'id': org.id,
                'name': org.name,
                'address': org.address,
                'phone': org.phone,
                'email': org.email
            } for org in orgs]
        })

@api.route('/client-organizations', methods=['POST'])
@handle_errors
def create_client_organization():
    data = request.get_json()
    client_org = add_client_organization(
        name=data['name'],
        address=data['address'],
        phone=data.get('phone'),
        email=data.get('email')
    )
    return jsonify({
        'success': True,
        'message': 'Client organization created successfully',
        'data': {'id': client_org.id}
    }), 201


@api.route('/training-requests', methods=['GET'])
@handle_errors
def get_training_requests():
    requests = get_all_training_requests()
    return jsonify({
        'success': True,
        'data': [{
            'id': req.id,
            'client_organization_id': req.client_organization_id,
            'course_id': req.course_id,
            'required_start_date': req.required_start_date.isoformat(),
            'required_end_date': req.required_end_date.isoformat(),
            'number_of_people': req.number_of_people,
        } for req in requests]
    })

@api.route('/training-requests', methods=['POST'])
@handle_errors
def create_training_request():
    data = request.get_json()
    request_obj = add_training_request(
        client_organization_id=data['client_organization_id'],
        course_id=data['course_id'],
        required_start_date=parse_date(data['required_start_date']),
        required_end_date=parse_date(data['required_end_date']),
        number_of_people=data['number_of_people']
    )
    return jsonify({
        'success': True,
        'message': 'Training request created successfully',
        'data': {'id': request_obj.id}
    }), 201

@api.route('/training-requests/<int:request_id>/employees', methods=['GET'])
@handle_errors
def get_request_employees(request_id):
    employees = get_employees_by_request(request_id)
    return jsonify({
        'success': True,
        'data': [{
            'id': emp.id,
            'full_name': emp.full_name,
            'position': emp.position
        } for emp in employees]
    })

@api.route('/training-requests/<int:request_id>/employees', methods=['POST'])
@handle_errors
def add_employee_to_request(request_id):
    data = request.get_json()
    employee = add_employee(
        training_request_id=request_id,
        full_name=data['full_name'],
        position=data['position']
    )
    return jsonify({
        'success': True,
        'message': 'Employee added successfully',
        'data': {'id': employee.id}
    }), 201


@api.route('/assignments', methods=['POST'])
@handle_errors
def create_assignment():
    data = request.get_json()
    assignment = add_assignment(
        teacher_id=data['teacher_id'],
        course_id=data['course_id'],
        document_number=data['document_number'],
        document_date=parse_date(data['document_date']),
        start_date=parse_date(data['start_date']),
        end_date=parse_date(data['end_date'])
    )
    return jsonify({
        'success': True,
        'message': 'Assignment created successfully',
        'data': {'id': assignment.id}
    }), 201


@api.route('/courses/<int:course_id>/prices', methods=['GET'])
@handle_errors
def get_course_prices(course_id):
    prices = get_course_price_history(course_id)
    return jsonify({
        'success': True,
        'data': [{
            'id': price.id,
            'document_number': price.document_number,
            'document_date': price.document_date.isoformat(),
            'price': float(price.price),
            'price_with_vat': float(price.price_with_vat),
            'valid_from': price.valid_from.isoformat(),
            'valid_to': price.valid_to.isoformat() if price.valid_to else None
        } for price in prices]
    })

@api.route('/courses/<int:course_id>/prices', methods=['POST'])
@handle_errors
def add_course_price(course_id):
    data = request.get_json()
    price = add_price_history(
        course_id=course_id,
        document_number=data['document_number'],
        price=data['price'],
        valid_from=parse_date(data['valid_from']),
        valid_to=parse_date(data['valid_to']) if data.get('valid_to') else None
    )
    return jsonify({
        'success': True,
        'message': 'Price added successfully',
        'data': {'id': price.id}
    }), 201


@api.route('/enums', methods=['GET'])
@handle_errors
def get_enums():
    return jsonify({
        'success': True,
        'data': {
            'course_types': [{'value': t.value, 'label': t.name} for t in CourseType],
            'teacher_categories': [{'value': c.value, 'label': c.name} for c in TeacherCategory],
            'genders': [{'value': 'M', 'label': 'Мужской'}, {'value': 'F', 'label': 'Женский'}]
        }
    })