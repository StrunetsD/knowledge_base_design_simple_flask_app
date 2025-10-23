from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date
import db_requests  

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_for_sessions'  

# --- Main Page & Dashboard ---
@app.route('/')
def index():
    """
    Displays the main dashboard with statistics.
    """
    try:
        stats = {
            'organizations_count': len(db_requests.get_all_organizations()),
            'courses_count': len(db_requests.get_all_courses()),
            'teachers_count': len(db_requests.get_all_teachers()),
            'requests_count': len(db_requests.get_all_training_requests())
        }
    except Exception as e:
        flash(f'Could not load statistics from the database: {e}', 'error')
        stats = {'organizations_count': 0, 'courses_count': 0, 'teachers_count': 0, 'requests_count': 0}
    return render_template('index.html', **stats)

# --- Organizations ---
@app.route('/organizations')
def organizations():
    """
    Displays a list of all organizations.
    """
    all_orgs = db_requests.get_all_organizations()
    return render_template('organizations.html', organizations=all_orgs)

@app.route('/organizations/add', methods=['GET', 'POST'])
def add_organization():
    """
    Handles adding a new organization.
    """
    if request.method == 'POST':
        try:
            db_requests.add_organization(
                code=request.form['code'],
                name=request.form['name'],
                address=request.form['address'],
                phone=request.form.get('phone'),
                email=request.form.get('email')
            )
            flash('Organization added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding organization: {e}', 'error')
        return redirect(url_for('organizations'))
    return render_template('organization_form.html')

@app.route('/organizations/edit/<int:org_id>', methods=['GET', 'POST'])
def edit_organization(org_id):
    """
    Handles editing an existing organization.
    """
    if request.method == 'POST':
        try:
            db_requests.update_organization(
                org_id=org_id,
                code=request.form['code'],
                name=request.form['name'],
                address=request.form['address'],
                phone=request.form.get('phone'),
                email=request.form.get('email')
            )
            flash('Organization information updated.', 'success')
        except Exception as e:
            flash(f'Error updating organization: {e}', 'error')
        return redirect(url_for('organizations'))
    
    org = db_requests.get_organization_by_id(org_id)
    return render_template('organization_form.html', organization=org)

@app.route('/organizations/delete/<int:org_id>')
def delete_organization(org_id):
    """
    Deletes an organization.
    """
    result = db_requests.delete_organization(org_id)
    if result:
        flash(f'Organization "{result[2]}" has been deleted.', 'success')
    else:
        flash('Could not delete organization. It might have associated courses.', 'error')
    return redirect(url_for('organizations'))

# --- Courses ---
@app.route('/courses')
def courses():
    """
    Displays a list of all courses.
    """
    all_courses = db_requests.get_all_courses()
    return render_template('courses.html', courses=all_courses)

@app.route('/courses/add', methods=['GET', 'POST'])
def add_course():
    """
    Handles adding a new course.
    """
    if request.method == 'POST':
        try:
            db_requests.add_course(
                code=request.form['code'],
                name=request.form['name'],
                type_id=request.form['type_id'],
                training_days=request.form['training_days'],
                max_students=request.form['max_students'],
                base_price=request.form['base_price'],
                organization_id=request.form['organization_id'],
                is_active='is_active' in request.form
            )
            flash('Course added successfully!', 'success')
        except Exception as e:
            flash(f'Error adding course: {e}', 'error')
        return redirect(url_for('courses'))
    
    # NOTE: You need a function in db_requests to get course types.
    # Using a placeholder for now.
    course_types = [(1, 'Professional Retraining'), (2, 'Advanced Training')]
    organizations_list = db_requests.get_all_organizations()
    return render_template('course_form.html', course_types=course_types, organizations=organizations_list)

@app.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    """
    Handles editing an existing course.
    """
    if request.method == 'POST':
        try:
            db_requests.update_course(
                course_id=course_id,
                code=request.form['code'],
                name=request.form['name'],
                type_id=request.form['type_id'],
                training_days=request.form['training_days'],
                max_students=request.form['max_students'],
                base_price=request.form['base_price'],
                organization_id=request.form['organization_id'],
                is_active='is_active' in request.form
            )
            flash('Course information updated.', 'success')
        except Exception as e:
            flash(f'Error updating course: {e}', 'error')
        return redirect(url_for('courses'))

    course = db_requests.get_course_by_id(course_id)
    course_types = [(1, 'Professional Retraining'), (2, 'Advanced Training')]  # Placeholder
    organizations_list = db_requests.get_all_organizations()
    return render_template('course_form.html', course=course, course_types=course_types, organizations=organizations_list)

@app.route('/courses/delete/<int:course_id>')
def delete_course(course_id):
    """
    Deletes a course.
    """
    result = db_requests.delete_course(course_id)
    if result:
        flash(f'Course "{result[2]}" has been deleted.', 'success')
    else:
        flash('Could not delete course. Check for dependencies like requests, assignments, or prices.', 'error')
    return redirect(url_for('courses'))

@app.route('/courses/<int:course_id>/add-price', methods=['GET', 'POST'])
def add_course_price(course_id):
    """
    Handles adding/updating course price information.
    """
    if request.method == 'POST':
        try:
            db_requests.add_price_document(
                document_number=request.form['document_number'],
                document_date=request.form['document_date'],
                price=request.form['price'],
                course_id=course_id
            )
            flash('Информация о стоимости курса обновлена!', 'success')
        except Exception as e:
            flash(f'Ошибка при обновлении стоимости: {e}', 'error')
        return redirect(url_for('courses'))
    
    course = db_requests.get_course_by_id(course_id)
    # Получить текущую цену курса, если есть
    current_price = db_requests.get_current_price(course_id)
    return render_template('course_price_form.html', 
                          course=course, 
                          current_price=current_price,
                          today=date.today().isoformat())

# --- Teachers ---
@app.route('/teachers')
def teachers():
    all_teachers = db_requests.get_all_teachers()
    return render_template('teachers.html', teachers=all_teachers)

@app.route('/teachers/add', methods=['GET', 'POST'])
def add_teacher():
    """
    Handles adding a new teacher.
    """
    if request.method == 'POST':
        try:
            db_requests.add_teacher(
                code=request.form['code'],
                full_name=request.form['full_name'],
                birth_date=request.form['birth_date'],
                gender=request.form.get('gender'),
                education=request.form.get('education'),
                category=request.form.get('category')
            )
            flash('Преподаватель добавлен успешно!', 'success')
        except Exception as e:
            flash(f'Ошибка при добавлении преподавателя: {e}', 'error')
        return redirect(url_for('teachers'))
    return render_template('teacher_form.html')

@app.route('/teachers/edit/<int:teacher_id>', methods=['GET', 'POST'])
def edit_teacher(teacher_id):
    """
    Handles editing an existing teacher.
    """
    if request.method == 'POST':
        try:
            db_requests.update_teacher(
                teacher_id=teacher_id,
                code=request.form['code'],
                full_name=request.form['full_name'],
                birth_date=request.form['birth_date'],
                gender=request.form.get('gender'),
                education=request.form.get('education'),
                category=request.form.get('category')
            )
            flash('Информация о преподавателе обновлена.', 'success')
        except Exception as e:
            flash(f'Ошибка при обновлении преподавателя: {e}', 'error')
        return redirect(url_for('teachers'))
    
    teacher = db_requests.get_teacher_by_id(teacher_id)
    return render_template('teacher_form.html', teacher=teacher)

@app.route('/teachers/delete/<int:teacher_id>')
def delete_teacher(teacher_id):
    """
    Deletes a teacher.
    """
    result = db_requests.delete_teacher(teacher_id)
    if result:
        flash(f'Преподаватель "{result[2]}" удален.', 'success')
    else:
        flash('Не удалось удалить преподавателя. Возможно, есть связанные записи.', 'error')
    return redirect(url_for('teachers'))

# --- Training Requests ---
@app.route('/training-requests')
def training_requests():
    all_requests = db_requests.get_all_training_requests()
    return render_template('training_requests.html', requests=all_requests)

@app.route('/training-requests/add', methods=['GET', 'POST'])
def add_training_request():
    """
    Handles adding a new training request.
    """
    if request.method == 'POST':
        try:
            db_requests.add_training_request_with_dates(
                request_number=request.form['request_number'],
                client_organization_id=request.form['client_organization_id'],
                course_id=request.form['course_id'],
                required_deadline=request.form['required_deadline'],
                total_students=request.form['total_students'],
                status=request.form['status'],
            )
            flash('Заявка на обучение добавлена успешно!', 'success')
        except Exception as e:
            flash(f'Ошибка при добавлении заявки: {e}', 'error')
        return redirect(url_for('training_requests'))
    
    client_organizations = db_requests.get_all_organizations()
    courses = db_requests.get_all_courses()
    return render_template('training_request_form.html', 
                          client_organizations=client_organizations, 
                          courses=courses)

@app.route('/training-requests/edit/<int:request_id>', methods=['GET', 'POST'])
def edit_training_request(request_id):
    """
    Handles editing an existing training request.
    """
    if request.method == 'POST':
        try:
            db_requests.update_training_request(
                request_id=request_id,
                request_number=request.form['request_number'],
                client_organization_id=request.form['client_organization_id'],
                course_id=request.form['course_id'],
                required_deadline=request.form['required_deadline'],
                total_students=request.form['total_students'],
                status=request.form['status'],
            )
            flash('Заявка на обучение обновлена.', 'success')
        except Exception as e:
            flash(f'Ошибка при обновлении заявки: {e}', 'error')
        return redirect(url_for('training_requests'))
    
    req = db_requests.get_training_request_by_id(request_id)
    client_organizations = db_requests.get_all_organizations()
    courses = db_requests.get_all_courses()
    return render_template('training_request_form.html', 
                          request=req,
                          client_organizations=client_organizations, 
                          courses=courses)

# --- Reports ---
@app.route('/reports/price-list', methods=['GET', 'POST'])
def price_list_report():
    """
    Handles the form for and display of the organization price list report.
    """
    if request.method == 'POST':
        org_id = request.form['organization_id']
        target_date = request.form['target_date']
        
        organization = db_requests.get_organization_by_id(org_id)
        price_list_data = db_requests.get_organization_price_list(org_id, target_date)
        
        return render_template('price_list_report.html', 
                               organization=organization, 
                               target_date=target_date, 
                               price_list=price_list_data)

    organizations_list = db_requests.get_all_organizations()
    return render_template('price_list_form.html', organizations=organizations_list, today=date.today().isoformat())

@app.route('/reports/group-filling', methods=['GET', 'POST'])
def group_filling_report():
    """
    Handles the form for and display of the group filling report.
    """
    if request.method == 'POST':
        course_id = request.form['course_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        course = db_requests.get_course_by_id(course_id)
        filling_data = db_requests.get_course_group_filling(course_id, start_date, end_date)
        
        return render_template('group_filling_report.html', 
                               course=course, 
                               start_date=start_date, 
                               end_date=end_date, 
                               filling_data=filling_data)

    courses_list = db_requests.get_all_courses()
    return render_template('group_filling_form.html', courses=courses_list)

@app.route('/reports/teacher-schedule', methods=['GET', 'POST'])
def teacher_schedule_report():
    """
    Handles the form for and display of the teacher schedule report.
    """
    if request.method == 'POST':
        teacher_id = request.form['teacher_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        teacher = db_requests.get_teacher_by_id(teacher_id)
        schedule_data = db_requests.get_teacher_schedule(teacher_id, start_date, end_date)

        return render_template('teacher_schedule_report.html',
                               teacher=teacher,
                               start_date=start_date,
                               end_date=end_date,
                               schedule=schedule_data)

    teachers_list = db_requests.get_all_teachers()
    return render_template('teacher_schedule_form.html', teachers=teachers_list)

if __name__ == '__main__':
    app.run(debug=True)