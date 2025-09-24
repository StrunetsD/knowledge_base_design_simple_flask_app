# app_frontend.py
import streamlit as st
from models import *
from db_conn import get_session
from datetime import date
from decimal import Decimal
from db_requests import *
from sqlalchemy.orm import joinedload

st.set_page_config(
    page_title="Тестирование запросов к БД",
    page_icon="🧪",
    layout="wide"
)

def main_menu():
    st.sidebar.title("🧪 Тестирование запросов")
    st.sidebar.info("Выберите раздел для тестирования")
    
    menu_options = [
        "📊 Обзор данных",
        "🏢 Организации",
        "📚 Курсы",
        "👨‍🏫 Преподаватели",
        "📝 Заявки на обучение",
        "💰 Прайс-лист",
        "📅 Расписание",
        "👥 Наполнение групп",
        "🔗 Связи преподавателей и курсов"  
    ]
    
    choice = st.sidebar.selectbox("Меню", menu_options)
    
    if choice == "📊 Обзор данных":
        show_dashboard()
    elif choice == "🏢 Организации":
        organizations_section()
    elif choice == "📚 Курсы":
        courses_section()
    elif choice == "👨‍🏫 Преподаватели":
        instructors_section()
    elif choice == "📝 Заявки на обучение":
        training_requests_section()
    elif choice == "💰 Прайс-лист":
        price_list_section()
    elif choice == "📅 Расписание":
        schedule_section()
    elif choice == "👥 Наполнение групп":
        groups_fill_section()
    elif choice == "🔗 Связи преподавателей и курсов": 
        course_instructor_links_section()

def show_dashboard():
    st.title("📊 Обзор данных в системе")
    
    with get_session() as session:
        col1, col2, col3, col4 = st.columns(4)
        
        org_count = session.query(Organization).count()
        col1.metric("Организации", org_count)
        
        course_count = session.query(Course).count()
        col2.metric("Курсы", course_count)
        
        instructor_count = session.query(Instructor).count()
        col3.metric("Преподаватели", instructor_count)
        
        request_count = session.query(TrainingRequest).count()
        col4.metric("Заявки", request_count)
        
        st.subheader("Последние организации")
        orgs = session.query(Organization).order_by(Organization.id.desc()).limit(5).all()
        for org in orgs:
            st.write(f"**{org.name}**-{org.address}")
        
        st.subheader("Последние курсы")
        courses = session.query(Course).order_by(Course.id.desc()).limit(5).all()
        for course in courses:
            st.write(f"**{course.name}**")

def organizations_section():
    st.title("🏢 Тестирование работы с организациями")
    
    with get_session() as session:
        tab1, tab2, tab3 = st.tabs(["Просмотр", "Добавить", "Редактировать/Удалить"])
        
        with tab1:
            st.subheader("Все организации")
            organizations = session.query(Organization).all()
            if organizations:
                for org in organizations:
                    with st.expander(f"{org.name} ({org.code})"):
                        st.write(f"**ID:** {org.id}")
                        st.write(f"**Адрес:** {org.address}")
                        st.write(f"**Телефон:** {org.phone or 'Не указан'}")
                        st.write(f"**Email:** {org.email or 'Не указан'}")
            else:
                st.info("Организации не найдены")
        
        with tab2:
            st.subheader("Добавить новую организацию")
            with st.form("add_org_form"):
                code = st.text_input("Код организации*")
                name = st.text_input("Название*")
                address = st.text_area("Адрес*")
                phone = st.text_input("Телефон")
                email = st.text_input("Email")
                
                if st.form_submit_button("Добавить организацию"):
                    if code and name and address:
                        try:
                            org = add_organization(session, code, name, address, phone, email)
                            st.success(f"Организация '{org.name}' добавлена успешно!")
                        except Exception as e:
                            st.error(f"Ошибка: {e}")
                    else:
                        st.error("Заполните обязательные поля (отмечены *)")
        
        with tab3:
            st.subheader("Редактирование и удаление")
            orgs = session.query(Organization).all()
            if orgs:
                org_options = {f"{org.name} ({org.code})": org.id for org in orgs}
                selected_org = st.selectbox("Выберите организацию", list(org_options.keys()))
                
                if selected_org:
                    org_id = org_options[selected_org]
                    org = session.get(Organization, org_id)
                    
                    with st.form("edit_org_form"):
                        st.write(f"Редактирование: {org.name}")
                        new_name = st.text_input("Название", value=org.name)
                        new_address = st.text_area("Адрес", value=org.address)
                        new_phone = st.text_input("Телефон", value=org.phone or "")
                        new_email = st.text_input("Email", value=org.email or "")
                        
                        if st.form_submit_button("Сохранить изменения"):
                            update_organization(session, org_id, 
                                              name=new_name,
                                              address=new_address,
                                              phone=new_phone,
                                              email=new_email)
                            st.success("Изменения сохранены!")
                    
                    if st.button("🗑️ Удалить организацию", type="secondary"):
                        if delete_organization(session, org_id):
                            st.success("Организация удалена!")
                            st.rerun()
                        else:
                            st.error("Не удалось удалить организацию")
            else:
                st.info("Нет организаций для редактирования")

def courses_section():
    st.title("📚 Тестирование работы с курсами")
    
    with get_session() as session:
        tab1, tab2, tab3, tab4 = st.tabs(["Просмотр", "Добавить", "Редактировать/Удалить", "Управление преподавателями"])
        
        with tab1:
            st.subheader("Все курсы")
            courses = session.query(Course).options(joinedload(Course.instructors)).all()
            if courses:
                for course in courses:
                    org = session.get(Organization, course.organization_id)
                    with st.expander(f"{course.name} ({course.code})"):
                        st.write(f"**Организация:** {org.name if org else 'Неизвестно'}")
                        st.write(f"**Тип:** {course.course_type}")
                        st.write(f"**Длительность:** {course.duration_days} дней")
                        st.write(f"**Макс. студентов:** {course.max_students}")
                        
                        if course.instructors:
                            st.write("**Преподаватели:**")
                            for instructor in course.instructors:
                                st.write(f"- {instructor.full_name}")
                        else:
                            st.write("**Преподаватели:** Не назначены")
            else:
                st.info("Курсы не найдены")
        
        with tab2:
            st.subheader("Добавить новый курс")
            orgs = session.query(Organization).all()
            if orgs:
                org_options = {org.name: org.id for org in orgs}
                
                with st.form("add_course_form"):
                    code = st.text_input("Код курса*")
                    name = st.text_input("Название*")
                    organization = st.selectbox("Организация*", list(org_options.keys()))
                    course_type = st.selectbox("Тип курса*", [ct.value for ct in CourseType])
                    duration = st.number_input("Длительность (дней)*", min_value=1, value=30)
                    max_students = st.number_input("Макс. студентов*", min_value=1, value=20)
                    
                    if st.form_submit_button("Добавить курс"):
                        if code and name:
                            try:
                                org_id = org_options[organization]
                                course = add_course(session, code, name, course_type, 
                                                  duration, max_students, org_id)
                                st.success(f"Курс '{course.name}' добавлен успешно!")
                            except Exception as e:
                                st.error(f"Ошибка: {e}")
                        else:
                            st.error("Заполните обязательные поля (отмечены *)")
            else:
                st.info("Сначала добавьте организации")
        
        with tab3:
            st.subheader("Редактирование и удаление")
            courses = session.query(Course).all()
            if courses:
                course_options = {f"{course.name} ({course.code})": course.id for course in courses}
                selected_course = st.selectbox("Выберите курс", list(course_options.keys()))
                
                if selected_course:
                    course_id = course_options[selected_course]
                    course = session.get(Course, course_id)
                    
                    with st.form("edit_course_form"):
                        st.write(f"Редактирование: {course.name}")
                        new_name = st.text_input("Название", value=course.name)
                        new_type = st.selectbox("Тип курса", [ct for ct in CourseType], format_func=lambda ct: ct.value)
                        index = [ct for ct in CourseType].index(course.course_type)
                        new_duration = st.number_input("Длительность (дней)", 
                                                     min_value=1, value=course.duration_days)
                        new_max_students = st.number_input("Макс. студентов", 
                                                         min_value=1, value=course.max_students)
                        
                        if st.form_submit_button("Сохранить изменения"):
                            update_course(session, course_id, 
                                         name=new_name,
                                         course_type=new_type,
                                         duration_days=new_duration,
                                         max_students=new_max_students)
                            st.success("Изменения сохранены!")
                    
                    if st.button("🗑️ Удалить курс", type="secondary"):
                        if delete_course(session, course_id):
                            st.success("Курс удален!")
                            st.rerun()
                        else:
                            st.error("Не удалось удалить курс")
            else:
                st.info("Нет курсов для редактирования")
        
        with tab4:
            st.subheader("Управление преподавателями курса")
            courses = session.query(Course).all()
            if courses:
                course_options = {f"{course.name} ({course.code})": course.id for course in courses}
                selected_course = st.selectbox("Выберите курс", list(course_options.keys()), key="course_select")
                
                if selected_course:
                    course_id = course_options[selected_course]
                    course = session.get(Course, course_id)
                    
                    st.write("Текущие преподаватели:")
                    if course.instructors:
                        for instructor in course.instructors:
                            st.write(f"- {instructor.full_name}")
                            if st.button(f"Удалить {instructor.full_name}", key=f"remove_{instructor.id}"):
                                remove_instructor_from_course(session, course_id, instructor.id)
                                st.success(f"Преподаватель {instructor.full_name} удален с курса")
                                st.rerun()
                    else:
                        st.info("На этот курс еще не назначены преподаватели")
                    
                    st.write("Добавить преподавателя:")
                    available_instructors = session.query(Instructor).filter(~Instructor.courses.any(id=course_id)).all()
                    
                    if available_instructors:
                        instructor_options = {instr.full_name: instr.id for instr in available_instructors}
                        selected_instructor = st.selectbox("Выберите преподавателя", list(instructor_options.keys()))
                        
                        if st.button("Добавить преподавателя"):
                            instructor_id = instructor_options[selected_instructor]
                            if assign_instructor_to_course(session, course_id, instructor_id):
                                st.success("Преподаватель добавлен на курс!")
                                st.rerun()
                            else:
                                st.error("Не удалось добавить преподавателя")
                    else:
                        st.info("Нет доступных преподавателей для добавления на этот курс")
            else:
                st.info("Нет курсов для управления")

def instructors_section():
    st.title("👨‍🏫 Тестирование работы с преподавателями")
    
    with get_session() as session:
        tab1, tab2, tab3, tab4 = st.tabs(["Просмотр", "Добавить", "Редактировать/Удалить", "Управление курсами"])
        
        with tab1:
            st.subheader("Все преподаватели")
            instructors = session.query(Instructor).options(joinedload(Instructor.courses)).all()
            if instructors:
                for instructor in instructors:
                    with st.expander(instructor.full_name):
                        st.write(f"**Номер:** {instructor.number}")
                        st.write(f"**Дата рождения:** {instructor.birth_date}")
                        st.write(f"**Пол:** {instructor.gender}")
                        st.write(f"**Образование:** {instructor.education}")
                        st.write(f"**Категория:** {instructor.category.value}")
                        
                        if instructor.courses:
                            st.write("**Курсы:**")
                            for course in instructor.courses:
                                st.write(f"- {course.name}")
                        else:
                            st.write("**Курсы:** Не назначен")
            else:
                st.info("Преподаватели не найдены")
        
        with tab2:
            st.subheader("Добавить нового преподавателя")
            with st.form("add_instructor_form"):
                number = st.text_input("Номер преподавателя*")
                full_name = st.text_input("ФИО*")
                birth_date = st.date_input("Дата рождения*", value=date(1980, 1, 1))
                gender_str = st.selectbox("Пол", ["М", "Ж"])
                education = st.text_input("Образование*")
                category_str = st.selectbox("Категория*", ["высшая", "первая", "вторая"])
                
                if st.form_submit_button("Добавить преподавателя"):
                    if number and full_name and education:
                        try:
                            instructor = add_instructor(
                                session,
                                number,
                                full_name,
                                birth_date,
                                gender_str,
                                education,
                                category_str
                            )
                            st.success(f"Преподаватель '{instructor.full_name}' добавлен успешно!")
                        except Exception as e:
                            st.error(f"Ошибка: {e}")
                    else:
                        st.error("Заполните обязательные поля (отмечены *)")
        
        with tab3:
            st.subheader("Редактирование и удаление")
            instructors = session.query(Instructor).all()
            if instructors:
                instructor_options = {f"{instr.full_name} ({instr.number})": instr.id for instr in instructors}
                selected_instructor = st.selectbox("Выберите преподавателя", list(instructor_options.keys()))
                
                if selected_instructor:
                    instructor_id = instructor_options[selected_instructor]
                    instructor = session.get(Instructor, instructor_id)
                    
                    with st.form("edit_instructor_form"):
                        st.write(f"Редактирование: {instructor.full_name}")
                        new_full_name = st.text_input("ФИО", value=instructor.full_name)
                        new_birth_date = st.date_input("Дата рождения", value=instructor.birth_date)
                        new_gender = st.selectbox("Пол", ["М", "Ж"], 
                                                index=0 if instructor.gender == "М" else 1)
                        new_education = st.text_input("Образование", value=instructor.education)
                        new_category = st.selectbox("Категория", 
                                                  ["высшая", "первая", "вторая"],
                                                  index=["высшая", "первая", "вторая"].index(instructor.category.value))
                        
                        if st.form_submit_button("Сохранить изменения"):
                            update_instructor(session, instructor_id, 
                                            full_name=new_full_name,
                                            birth_date=new_birth_date,
                                            gender=new_gender,
                                            education=new_education,
                                            category=new_category)
                            st.success("Изменения сохранены!")
                    
                    if st.button("🗑️ Удалить преподавателя", type="secondary"):
                        if delete_instructor(session, instructor_id):
                            st.success("Преподаватель удален!")
                            st.rerun()
                        else:
                            st.error("Не удалось удалить преподавателя")
            else:
                st.info("Нет преподавателей для редактирования")
        
        with tab4:
            st.subheader("Управление курсами преподавателя")
            instructors = session.query(Instructor).all()
            if instructors:
                instructor_options = {f"{instr.full_name} ({instr.number})": instr.id for instr in instructors}
                selected_instructor = st.selectbox("Выберите преподавателя", list(instructor_options.keys()), key="instructor_select")
                
                if selected_instructor:
                    instructor_id = instructor_options[selected_instructor]
                    instructor = session.get(Instructor, instructor_id)
                    
                    st.write("Текущие курсы:")
                    if instructor.courses:
                        for course in instructor.courses:
                            st.write(f"- {course.name}")
                            if st.button(f"Удалить {course.name}", key=f"remove_{course.id}"):
                                remove_instructor_from_course(session, course.id, instructor_id)
                                st.success(f"Преподаватель удален с курса {course.name}")
                                st.rerun()
                    else:
                        st.info("Этот преподаватель еще не назначен на курсы")
                    
                    st.write("Добавить курс:")
                    available_courses = session.query(Course).filter(~Course.instructors.any(id=instructor_id)).all()
                    
                    if available_courses:
                        course_options = {course.name: course.id for course in available_courses}
                        selected_course = st.selectbox("Выберите курс", list(course_options.keys()))
                        
                        if st.button("Добавить курс"):
                            course_id = course_options[selected_course]
                            if assign_instructor_to_course(session, course_id, instructor_id):
                                st.success("Преподаватель добавлен на курс!")
                                st.rerun()
                            else:
                                st.error("Не удалось добавить преподавателя на курс")
                    else:
                        st.info("Нет доступных курсов для этого преподавателя")
            else:
                st.info("Нет преподавателей для управления")

def training_requests_section():
    st.title("📝 Тестирование заявок на обучение")
    
    with get_session() as session:
        tab1, tab2 = st.tabs(["Просмотр заявок", "Добавить заявку"])
        
        with tab1:
            st.subheader("Все заявки на обучение")
            requests = session.query(TrainingRequest).options(
                joinedload(TrainingRequest.client_organization),
                joinedload(TrainingRequest.course)
            ).all()
            
            if requests:
                for req in requests:
                    with st.expander(f"Заявка #{req.id}"):
                        st.write(f"**Организация:** {req.client_organization.name}")
                        st.write(f"**Курс:** {req.course.name}")
                        st.write(f"**Период:** {req.requested_start_date} - {req.requested_end_date}")
                        st.write(f"**Количество студентов:** {req.number_of_students}")
                        st.write(f"**Контакты:** {req.contact_phone}, {req.contact_email}")
            else:
                st.info("Заявки на обучение не найдены")
        
        with tab2:
            st.subheader("Добавить новую заявку")
            orgs = session.query(Organization).all()
            courses = session.query(Course).all()
            
            if orgs and courses:
                org_options = {org.name: org.id for org in orgs}
                course_options = {course.name: course.id for course in courses}
                
                with st.form("add_request_form"):
                    organization = st.selectbox("Организация*", list(org_options.keys()))
                    course = st.selectbox("Курс*", list(course_options.keys()))
                    start_date = st.date_input("Дата начала*", value=date.today())
                    end_date = st.date_input("Дата окончания*", value=date.today())
                    students_count = st.number_input("Количество студентов*", min_value=1, value=10)
                    contact_phone = st.text_input("Контактный телефон*")
                    contact_email = st.text_input("Контактный email*")
                    
                    if st.form_submit_button("Добавить заявку"):
                        try:
                            org_id = org_options[organization]
                            course_id = course_options[course]
                            request = add_training_request(session, org_id, course_id, 
                                                         start_date, end_date, students_count,
                                                         contact_phone, contact_email)
                            st.success(f"Заявка #{request.id} добавлена успешно!")
                        except Exception as e:
                            st.error(f"Ошибка: {e}")
            else:
                st.info("Сначала добавьте организации и курсы")

def price_list_section():
    st.title("💰 Тестирование прайс-листа")
    
    with get_session() as session:
        st.subheader("Прайс-лист на текущую дату")
        
        orgs = session.query(Organization).all()
        if orgs:
            org_options = {org.name: org.id for org in orgs}
            selected_org = st.selectbox("Выберите организацию", list(org_options.keys()))
            target_date = st.date_input("Дата для просмотра цен", value=date.today())
            
            if st.button("Показать прайс-лист"):
                org_id = org_options[selected_org]
                prices = get_price_list(session, org_id, target_date)
                
                if prices:
                    st.write(f"Прайс-лист организации '{selected_org}' на {target_date}:")
                    for price in prices:
                        st.write(f"**{price.name}** - {price.duration_days} дней: "
                               f"{price.price} руб. (с НДС: {price.price_with_vat:.2f} руб.)")
                else:
                    st.info("Цены не найдены для выбранной даты.")
        else:
            st.info("Сначала добавьте организации.")

def schedule_section():
    st.title("📅 Тестирование расписания")
    
    with get_session() as session:
        st.subheader("Расписание преподавателя")
        
        instructors = session.query(Instructor).all()
        if instructors:
            instructor_options = {instructor.full_name: instructor.id for instructor in instructors}
            selected_instructor = st.selectbox("Выберите преподавателя", list(instructor_options.keys()))
            start_date = st.date_input("Дата начала", value=date.today())
            end_date = st.date_input("Дата окончания", value=date.today())
            
            if st.button("Показать расписание"):
                instructor_id = instructor_options[selected_instructor]
                schedule = get_instructor_schedule(session, instructor_id, start_date, end_date)
                
                if schedule:
                    st.write(f"Расписание преподавателя '{selected_instructor}' с {start_date} по {end_date}:")
                    for item in schedule:
                        st.write(f"**{item.name}**: {item.start_date} - {item.end_date}")
                else:
                    st.info("Расписание не найдено для выбранного периода.")
        else:
            st.info("Сначала добавьте преподавателей.")

def groups_fill_section():
    st.title("👥 Тестирование наполнения групп")
    
    with get_session() as session:
        st.subheader("Наполнение групп для курса")
        
        courses = session.query(Course).all()
        if courses:
            course_options = {course.name: course.id for course in courses}
            selected_course = st.selectbox("Выберите курс", list(course_options.keys()))
            start_date = st.date_input("Дата начала", value=date.today())
            end_date = st.date_input("Дата окончания", value=date.today())
            
            if st.button("Показать наполнение групп"):
                course_id = course_options[selected_course]
                groups_fill = get_course_groups_fill(session, course_id, start_date, end_date)
                
                if groups_fill:
                    st.write(f"Наполнение групп для курса '{selected_course}' с {start_date} по {end_date}:")
                    for group in groups_fill:
                        status = "полная" if group['is_full'] else "неполная"
                        st.write(f"Группа #{group['request_id']} ({group['start_date']} - {group['end_date']}): "
                                  f"{group['student_count']}/{group['max_students']} ({status})")
                else:
                    st.info("Нет данных о наполнении групп для выбранного периода.")
        else:
            st.info("Сначала добавьте курсы.")

def course_instructor_links_section():
    st.title("🔗 Управление связями преподавателей и курсов")
    
    with get_session() as session:
        tab1, tab2 = st.tabs(["Назначить преподавателя на курс", "Просмотр всех связей"])
        
        with tab1:
            st.subheader("Назначить преподавателя на курс")
            
            courses = session.query(Course).all()
            instructors = session.query(Instructor).all()
            
            if courses and instructors:
                course_options = {f"{course.name} ({course.code})": course.id for course in courses}
                instructor_options = {f"{instr.full_name} ({instr.number})": instr.id for instr in instructors}
                
                selected_course = st.selectbox("Выберите курс", list(course_options.keys()))
                selected_instructor = st.selectbox("Выберите преподавателя", list(instructor_options.keys()))
                
                if st.button("Назначить преподавателя на курс"):
                    course_id = course_options[selected_course]
                    instructor_id = instructor_options[selected_instructor]
                    
                    course = session.get(Course, course_id)
                    instructor = session.get(Instructor, instructor_id)
                    
                    if instructor in course.instructors:
                        st.warning("Этот преподаватель уже назначен на выбранный курс")
                    else:
                        if assign_instructor_to_course(session, course_id, instructor_id):
                            st.success(f"Преподаватель {selected_instructor} назначен на курс {selected_course}")
                        else:
                            st.error("Не удалось назначить преподавателя на курс")
            else:
                st.info("Сначала добавьте курсы и преподавателей")
        
        with tab2:
            st.subheader("Все связи преподавателей и курсов")
            
            courses = session.query(Course).options(joinedload(Course.instructors)).all()
            
            if courses:
                for course in courses:
                    with st.expander(f"{course.name} ({course.code})"):
                        if course.instructors:
                            st.write("**Преподаватели:**")
                            for instructor in course.instructors:
                                st.write(f"- {instructor.full_name} ({instructor.number})")
                                
                                if st.button(f"Удалить связь с {instructor.full_name}", 
                                           key=f"remove_{course.id}_{instructor.id}"):
                                    if remove_instructor_from_course(session, course.id, instructor.id):
                                        st.success("Связь удалена")
                                        st.rerun()
                                    else:
                                        st.error("Не удалось удалить связь")
                        else:
                            st.info("На этот курс не назначены преподаватели")
            else:
                st.info("Курсы не найдены")

if __name__ == "__main__":
    main_menu()