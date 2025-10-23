from config import settings
from db_conn import db

def add_organization(code, name, address, phone=None, email=None):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            INSERT INTO organizations (code, name, address, phone, email)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, code, name;
            """,
            (code, name, address, phone, email))
        result = cur.fetchone()
        return result

def get_all_organizations():
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT id, code, name, address, phone, email 
            FROM organizations 
            ORDER BY id;
            """)
        result = cur.fetchall()
        return result

def get_organization_by_id(org_id):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT id, code, name, address, phone, email 
            FROM organizations 
            WHERE id = %s;
            """,
            (org_id,))
        result = cur.fetchone()
        return result

def update_organization(org_id, code=None, name=None, address=None, phone=None, email=None):
    connection = db.get_connection()
    
    update_fields = []
    params = []
    
    if code is not None:
        update_fields.append("code = %s")
        params.append(code)
    if name is not None:
        update_fields.append("name = %s")
        params.append(name)
    if address is not None:
        update_fields.append("address = %s")
        params.append(address)
    if phone is not None:
        update_fields.append("phone = %s")
        params.append(phone)
    if email is not None:
        update_fields.append("email = %s")
        params.append(email)
        
    if not update_fields:
        return None
        
    params.append(org_id)
    
    query = f"""
        UPDATE organizations 
        SET {', '.join(update_fields)}
        WHERE id = %s
        RETURNING id, code, name, address, phone, email;
    """
    
    with connection.cursor() as cur:
        cur.execute(query, params)
        result = cur.fetchone()
        return result

def delete_organization(org_id):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM courses WHERE organization_id = %s;
            """,
            (org_id,))
        course_count = cur.fetchone()[0]
        
        if course_count > 0:
            return None
            
        cur.execute("""
            DELETE FROM organizations 
            WHERE id = %s 
            RETURNING id, code, name;
            """,
            (org_id,))
        result = cur.fetchone()
        return result

def add_course(code, name, type_id, training_days, max_students, base_price, organization_id, is_active=True):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            INSERT INTO courses (code, name, type_id, training_days, max_students, base_price, organization_id, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, code, name;
            """,
            (code, name, type_id, training_days, max_students, base_price, organization_id, is_active))
        result = cur.fetchone()
        return result

def add_course_dates(training_request_id, start_date, end_date):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            INSERT INTO course_dates (training_request_id, start_date, end_date)
            VALUES (%s, %s, %s)
            RETURNING id, start_date, end_date;
            """,
            (training_request_id, start_date, end_date))
        result = cur.fetchone()
        return result

def get_course_dates_by_request(training_request_id):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT id, start_date, end_date, created_at
            FROM course_dates 
            WHERE training_request_id = %s
            ORDER BY start_date;
            """,
            (training_request_id,))
        result = cur.fetchall()
        return result

def update_course_dates(course_dates_id, start_date=None, end_date=None):
    connection = db.get_connection()
    
    update_fields = []
    params = []
    
    if start_date is not None:
        update_fields.append("start_date = %s")
        params.append(start_date)
    if end_date is not None:
        update_fields.append("end_date = %s")
        params.append(end_date)
        
    if not update_fields:
        return None
        
    params.append(course_dates_id)
    
    query = f"""
        UPDATE course_dates 
        SET {', '.join(update_fields)}
        WHERE id = %s
        RETURNING id, start_date, end_date;
    """
    
    with connection.cursor() as cur:
        cur.execute(query, params)
        result = cur.fetchone()
        return result

def get_course_dates_by_course(course_id):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT cd.id, cd.start_date, cd.end_date, 
                   tr.request_number, co.name as client_organization
            FROM course_dates cd
            JOIN training_requests tr ON cd.training_request_id = tr.id
            JOIN client_organizations co ON tr.client_organization_id = co.id
            WHERE tr.course_id = %s
            ORDER BY cd.start_date;
            """,
            (course_id,))
        result = cur.fetchall()
        return result
    
def get_all_courses():
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.code, c.name, ct.name as type_name, c.training_days, 
                   c.max_students, c.base_price, c.vat_price, o.name as organization_name, c.is_active
            FROM courses c
            JOIN course_types ct ON c.type_id = ct.id
            JOIN organizations o ON c.organization_id = o.id
            ORDER BY c.id;
            """)
        result = cur.fetchall()
        return result

def get_course_by_id(course_id):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.code, c.name, c.type_id, c.training_days, c.max_students,
                   c.base_price, c.vat_price, c.organization_id, c.is_active,
                   ct.name as type_name, o.name as organization_name
            FROM courses c
            JOIN course_types ct ON c.type_id = ct.id
            JOIN organizations o ON c.organization_id = o.id
            WHERE c.id = %s;
            """,
            (course_id,))
        result = cur.fetchone()
        return result

def update_course(course_id, code=None, name=None, type_id=None, training_days=None, 
                 max_students=None, base_price=None, organization_id=None, is_active=None):
    connection = db.get_connection()
    
    update_fields = []
    params = []
    
    if code is not None:
        update_fields.append("code = %s")
        params.append(code)
    if name is not None:
        update_fields.append("name = %s")
        params.append(name)
    if type_id is not None:
        update_fields.append("type_id = %s")
        params.append(type_id)
    if training_days is not None:
        update_fields.append("training_days = %s")
        params.append(training_days)
    if max_students is not None:
        update_fields.append("max_students = %s")
        params.append(max_students)
    if base_price is not None:
        update_fields.append("base_price = %s")
        params.append(base_price)
    if organization_id is not None:
        update_fields.append("organization_id = %s")
        params.append(organization_id)
    if is_active is not None:
        update_fields.append("is_active = %s")
        params.append(is_active)
        
    if not update_fields:
        return None
        
    params.append(course_id)
    
    query = f"""
        UPDATE courses 
        SET {', '.join(update_fields)}
        WHERE id = %s
        RETURNING id, code, name;
    """
    
    with connection.cursor() as cur:
        cur.execute(query, params)
        result = cur.fetchone()
        return result

def delete_course(course_id):
    connection = db.get_connection()
    with connection.cursor() as cur:
        # Проверяем наличие зависимых записей одним запросом
        cur.execute("""
            SELECT 
                (SELECT COUNT(*) FROM training_requests WHERE course_id = %s) as requests_count,
                (SELECT COUNT(*) FROM teacher_assignments WHERE course_id = %s) as assignments_count,
                (SELECT COUNT(*) FROM price_documents WHERE course_id = %s) as prices_count,
                (SELECT COUNT(*) FROM course_lead_teacher WHERE course_id = %s) as lead_teachers_count,
                (SELECT COUNT(*) FROM course_tag_relationship WHERE course_id = %s) as tags_count;
            """,
            (course_id, course_id, course_id, course_id, course_id))
        
        counts = cur.fetchone()
        total_dependencies = sum(counts)
        
        if total_dependencies > 0:
            print(f"Нельзя удалить курс: найдены зависимости - "
                  f"заявки: {counts[0]}, назначения: {counts[1]}, "
                  f"цены: {counts[2]}, ведущие преподаватели: {counts[3]}, "
                  f"теги: {counts[4]}")
            return None

        cur.execute("""
            DELETE FROM courses 
            WHERE id = %s 
            RETURNING id, code, name;
            """,
            (course_id,))
        result = cur.fetchone()
        return result

def get_courses_by_organization(org_id):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.code, c.name, ct.name as type_name, c.training_days,
                   c.max_students, c.base_price, c.is_active
            FROM courses c
            JOIN course_types ct ON c.type_id = ct.id
            WHERE c.organization_id = %s
            ORDER BY c.name;
            """,
            (org_id,))
        result = cur.fetchall()
        return result

def search_organizations(search_term):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT id, code, name, address, phone, email 
            FROM organizations 
            WHERE name ILIKE %s OR code ILIKE %s
            ORDER BY name;
            """,
            (f'%{search_term}%', f'%{search_term}%'))
        result = cur.fetchall()
        return result
    
def search_courses(search_term):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.code, c.name, ct.name as type_name, o.name as organization_name
            FROM courses c
            JOIN course_types ct ON c.type_id = ct.id
            JOIN organizations o ON c.organization_id = o.id
            WHERE c.name ILIKE %s OR c.code ILIKE %s
            ORDER BY c.name;
            """,
            (f'%{search_term}%', f'%{search_term}%'))
        result = cur.fetchall()
        return result


def add_price_document(document_number, document_date, price, course_id):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            INSERT INTO price_documents (document_number, document_date, price, course_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id, document_number, document_date, price;
            """,
            (document_number, document_date, price, course_id))
        result = cur.fetchone()
        return result

def get_price_documents_by_course(course_id):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT id, document_number, document_date, price, created_at
            FROM price_documents 
            WHERE course_id = %s
            ORDER BY document_date DESC;
            """,
            (course_id,))
        result = cur.fetchall()
        return result

def get_current_price(course_id):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT price, document_number, document_date
            FROM price_documents 
            WHERE course_id = %s
            ORDER BY document_date DESC
            LIMIT 1;
            """,
            (course_id,))
        result = cur.fetchone()
        return result


def add_teacher(code, full_name, birth_date, gender=None, education=None, category=None):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            INSERT INTO teachers (code, full_name, birth_date, gender, education, category)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, code, full_name;
            """,
            (code, full_name, birth_date, gender, education, category))
        result = cur.fetchone()
        return result

def get_all_teachers():
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT id, code, full_name, birth_date, gender, education, category
            FROM teachers 
            ORDER BY full_name;
            """)
        result = cur.fetchall()
        return result

def get_teacher_by_id(teacher_id):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT id, code, full_name, birth_date, gender, education, category
            FROM teachers 
            WHERE id = %s;
            """,
            (teacher_id,))
        result = cur.fetchone()
        return result

def update_teacher(teacher_id, code=None, full_name=None, birth_date=None, gender=None, education=None, category=None):
    connection = db.get_connection()
    
    update_fields = []
    params = []
    
    if code is not None:
        update_fields.append("code = %s")
        params.append(code)
    if full_name is not None:
        update_fields.append("full_name = %s")
        params.append(full_name)
    if birth_date is not None:
        update_fields.append("birth_date = %s")
        params.append(birth_date)
    if gender is not None:
        update_fields.append("gender = %s")
        params.append(gender)
    if education is not None:
        update_fields.append("education = %s")
        params.append(education)
    if category is not None:
        update_fields.append("category = %s")
        params.append(category)
        
    if not update_fields:
        return None
        
    params.append(teacher_id)
    
    query = f"""
        UPDATE teachers 
        SET {', '.join(update_fields)}
        WHERE id = %s
        RETURNING id, code, full_name;
    """
    
    with connection.cursor() as cur:
        cur.execute(query, params)
        result = cur.fetchone()
        return result

def delete_teacher(teacher_id):
    connection = db.get_connection()
    with connection.cursor() as cur:
        tables_to_check = [
            "teacher_assignments",
            "course_lead_teacher", 
            "teacher_organization"
        ]
        
        for table in tables_to_check:
            if table == "teacher_assignments":
                cur.execute(f"SELECT COUNT(*) FROM {table} WHERE teacher_id = %s;", (teacher_id,))
            elif table == "course_lead_teacher":
                cur.execute(f"SELECT COUNT(*) FROM {table} WHERE lead_teacher_id = %s;", (teacher_id,))
            elif table == "teacher_organization":
                cur.execute(f"SELECT COUNT(*) FROM {table} WHERE teacher_id = %s;", (teacher_id,))
            count = cur.fetchone()[0]
            if count > 0:
                return None

        cur.execute("""
            DELETE FROM teachers 
            WHERE id = %s 
            RETURNING id, code, full_name;
            """,
            (teacher_id,))
        result = cur.fetchone()
        return result

def search_teachers(search_term):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT id, code, full_name, birth_date, gender, category
            FROM teachers 
            WHERE full_name ILIKE %s OR code ILIKE %s
            ORDER BY full_name;
            """,
            (f'%{search_term}%', f'%{search_term}%'))
        result = cur.fetchall()
        return result

def add_training_request_with_dates(request_number, client_organization_id, course_id, 
                                  required_deadline, total_students, start_date, end_date, status='новая'):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            INSERT INTO training_requests (request_number, client_organization_id, course_id, 
                                         required_deadline, total_students, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, request_number, request_date, status;
            """,
            (request_number, client_organization_id, course_id, required_deadline, total_students, status))
        request_result = cur.fetchone()
        
        if request_result:
            cur.execute("""
                INSERT INTO course_dates (training_request_id, start_date, end_date)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (request_result[0], start_date, end_date))
        
        return request_result

def get_all_training_requests():
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT tr.id, tr.request_number, tr.request_date, 
                   co.name as client_org, c.name as course_name,
                   tr.required_deadline, tr.total_students, tr.status
            FROM training_requests tr
            JOIN client_organizations co ON tr.client_organization_id = co.id
            JOIN courses c ON tr.course_id = c.id
            ORDER BY tr.request_date DESC;
            """)
        result = cur.fetchall()
        return result

def get_training_request_by_id(request_id):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT tr.id, tr.request_number, tr.request_date, 
                   tr.client_organization_id, tr.course_id, tr.required_deadline,
                   tr.total_students, tr.status,
                   co.name as client_org, c.name as course_name,
                   cd.start_date, cd.end_date, cd.id as course_dates_id
            FROM training_requests tr
            JOIN client_organizations co ON tr.client_organization_id = co.id
            JOIN courses c ON tr.course_id = c.id
            LEFT JOIN course_dates cd ON tr.id = cd.training_request_id
            WHERE tr.id = %s;
            """,
            (request_id,))
        result = cur.fetchone()
        return result

def update_training_request(request_id, request_number=None, client_organization_id=None, course_id=None, 
                          required_deadline=None, total_students=None, status=None):
    connection = db.get_connection()
    
    update_fields = []
    params = []
    
    if request_number is not None:
        update_fields.append("request_number = %s")
        params.append(request_number)
    if client_organization_id is not None:
        update_fields.append("client_organization_id = %s")
        params.append(client_organization_id)
    if course_id is not None:
        update_fields.append("course_id = %s")
        params.append(course_id)
    if required_deadline is not None:
        update_fields.append("required_deadline = %s")
        params.append(required_deadline)
    if total_students is not None:
        update_fields.append("total_students = %s")
        params.append(total_students)
    if status is not None:
        update_fields.append("status = %s")
        params.append(status)
        
    if not update_fields:
        return None
        
    params.append(request_id)
    
    query = f"""
        UPDATE training_requests 
        SET {', '.join(update_fields)}
        WHERE id = %s
        RETURNING id, request_number, status;
    """
    
    with connection.cursor() as cur:
        cur.execute(query, params)
        result = cur.fetchone()
        return result

def get_training_requests_by_status(status):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT tr.id, tr.request_number, tr.request_date, 
                   co.name as client_org, c.name as course_name,
                   tr.total_students
            FROM training_requests tr
            JOIN client_organizations co ON tr.client_organization_id = co.id
            JOIN courses c ON tr.course_id = c.id
            WHERE tr.status = %s
            ORDER BY tr.request_date;
            """,
            (status,))
        result = cur.fetchall()
        return result


def add_client_organization(name, address, phone=None, email=None):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            INSERT INTO client_organizations (name, address, phone, email)
            VALUES (%s, %s, %s, %s)
            RETURNING id, name, address;
            """,
            (name, address, phone, email))
        result = cur.fetchone()
        return result

def get_all_client_organizations():
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT id, name, address, phone, email
            FROM client_organizations 
            ORDER BY name;
            """)
        result = cur.fetchall()
        return result


def get_organization_price_list(org_id, target_date):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT 
                c.code as course_code,
                c.name as course_name,
                ct.name as course_type,
                c.training_days,
                COALESCE(pd.price, c.base_price) as current_price,
                COALESCE(pd.price, c.base_price) * 1.2 as price_with_vat,
                pd.document_number,
                pd.document_date
            FROM courses c
            JOIN course_types ct ON c.type_id = ct.id
            LEFT JOIN price_documents pd ON c.id = pd.course_id 
                AND pd.document_date = (
                    SELECT MAX(document_date) 
                    FROM price_documents 
                    WHERE course_id = c.id AND document_date <= %s
                )
            WHERE c.organization_id = %s AND c.is_active = true
            ORDER BY c.name;
            """,
            (target_date, org_id))
        result = cur.fetchall()
        return result

def get_teacher_schedule(teacher_id, start_date, end_date):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT 
                c.name as course_name,
                ta.start_date,
                ta.end_date,
                s.lesson_date,
                s.start_time,
                s.end_time
            FROM teacher_assignments ta
            JOIN courses c ON ta.course_id = c.id
            JOIN schedule s ON ta.id = s.teacher_assignment_id
            WHERE ta.teacher_id = %s 
                AND s.lesson_date BETWEEN %s AND %s
            ORDER BY s.lesson_date, s.start_time;
            """,
            (teacher_id, start_date, end_date))
        result = cur.fetchall()
        return result

def get_course_group_filling(course_id, start_date, end_date):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("SELECT max_students FROM courses WHERE id = %s;", (course_id,))
        max_students = cur.fetchone()[0]
        
        cur.execute("""
            SELECT 
                COUNT(*) as total_groups,
                SUM(tr.total_students) as total_students,
                COUNT(CASE WHEN tr.total_students >= c.max_students THEN 1 END) as full_groups,
                COUNT(CASE WHEN tr.total_students < c.max_students THEN 1 END) as not_full_groups
            FROM training_requests tr
            JOIN courses c ON tr.course_id = c.id
            WHERE tr.course_id = %s 
                AND tr.request_date BETWEEN %s AND %s
                AND tr.status IN ('подтверждена', 'завершена');
            """,
            (course_id, start_date, end_date))
        group_stats = cur.fetchone()
        
        cur.execute("""
            SELECT 
                tr.request_number,
                tr.request_date,
                tr.total_students,
                tr.status,
                CASE 
                    WHEN tr.total_students >= c.max_students THEN 'Полностью набрана'
                    ELSE 'Не полностью набрана'
                END as filling_status,
                ROUND((tr.total_students::decimal / c.max_students) * 100, 2) as filling_percentage
            FROM training_requests tr
            JOIN courses c ON tr.course_id = c.id
            WHERE tr.course_id = %s 
                AND tr.request_date BETWEEN %s AND %s
                AND tr.status IN ('подтверждена', 'завершена')
            ORDER BY tr.request_date;
            """,
            (course_id, start_date, end_date))
        group_details = cur.fetchall()
        
        return {
            'max_students': max_students,
            'total_groups': group_stats[0],
            'total_students': group_stats[1],
            'full_groups': group_stats[2],
            'not_full_groups': group_stats[3],
            'group_details': group_details
        }

def get_course_schedule(course_id, start_date, end_date):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT 
                s.lesson_date,
                s.start_time,
                s.end_time,
                t.full_name as teacher_name
            FROM teacher_assignments ta
            JOIN schedule s ON ta.id = s.teacher_assignment_id
            JOIN teachers t ON ta.teacher_id = t.id
            WHERE ta.course_id = %s 
                AND s.lesson_date BETWEEN %s AND %s
            ORDER BY s.lesson_date, s.start_time;
            """,
            (course_id, start_date, end_date))
        result = cur.fetchall()
        return result

def get_teacher_courses(teacher_id):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT DISTINCT
                c.id,
                c.name,
                c.code,
                ta.start_date,
                ta.end_date
            FROM teacher_assignments ta
            JOIN courses c ON ta.course_id = c.id
            WHERE ta.teacher_id = %s 
                AND ta.end_date >= CURRENT_DATE
            ORDER BY ta.start_date;
            """,
            (teacher_id,))
        result = cur.fetchall()
        return result

def add_teacher_assignment(document_number, document_date, teacher_id, course_id, start_date, end_date):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            INSERT INTO teacher_assignments (document_number, document_date, teacher_id, course_id, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, document_number, start_date, end_date;
            """,
            (document_number, document_date, teacher_id, course_id, start_date, end_date))
        result = cur.fetchone()
        return result

def get_teacher_assignments(teacher_id=None, course_id=None):
    connection = db.get_connection()
    with connection.cursor() as cur:
        query = """
            SELECT ta.id, ta.document_number, ta.document_date, 
                   t.full_name as teacher_name, c.name as course_name,
                   ta.start_date, ta.end_date
            FROM teacher_assignments ta
            JOIN teachers t ON ta.teacher_id = t.id
            JOIN courses c ON ta.course_id = c.id
            WHERE 1=1
        """
        params = []
        
        if teacher_id:
            query += " AND ta.teacher_id = %s"
            params.append(teacher_id)
            
        if course_id:
            query += " AND ta.course_id = %s"
            params.append(course_id)
            
        query += " ORDER BY ta.start_date DESC;"
        
        cur.execute(query, params)
        result = cur.fetchall()
        return result

def set_course_lead_teacher(course_id, lead_teacher_id):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("DELETE FROM course_lead_teacher WHERE course_id = %s;", (course_id,))
        
        cur.execute("""
            INSERT INTO course_lead_teacher (course_id, lead_teacher_id)
            VALUES (%s, %s)
            RETURNING id, course_id, lead_teacher_id;
            """,
            (course_id, lead_teacher_id))
        result = cur.fetchone()
        return result

def get_course_lead_teacher(course_id):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT clt.id, clt.course_id, clt.lead_teacher_id, clt.assigned_date,
                   t.full_name as teacher_name, t.code as teacher_code
            FROM course_lead_teacher clt
            JOIN teachers t ON clt.lead_teacher_id = t.id
            WHERE clt.course_id = %s;
            """,
            (course_id,))
        result = cur.fetchone()
        return result

def add_schedule_entry(teacher_assignment_id, lesson_date, start_time, end_time):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            INSERT INTO schedule (teacher_assignment_id, lesson_date, start_time, end_time)
            VALUES (%s, %s, %s, %s)
            RETURNING id, lesson_date, start_time, end_time;
            """,
            (teacher_assignment_id, lesson_date, start_time, end_time))
        result = cur.fetchone()
        return result

def get_schedule_by_assignment(teacher_assignment_id):
    connection = db.get_connection()
    with connection.cursor() as cur:
        cur.execute("""
            SELECT id, lesson_date, start_time, end_time
            FROM schedule 
            WHERE teacher_assignment_id = %s
            ORDER BY lesson_date, start_time;
            """,
            (teacher_assignment_id,))
        result = cur.fetchall()
        return result
