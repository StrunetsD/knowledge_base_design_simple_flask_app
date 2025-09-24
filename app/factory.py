# populate_test_data.py
from datetime import date
from db_conn import get_session
from models import Base, Organization, Instructor, Course, CoursePrice, AssignmentDocument, TrainingRequest, Student, CourseType, InstructorCategory, course_instructor_association

def create_test_data():
    with get_session() as session:
        organizations = [
            Organization(
                code="org_001",
                name="ООО 'Рога и копыта'",
                address="г. Москва, ул. Пушкина, д. 10",
                phone="+7 (495) 123-45-67",
                email="info@rogaikopyta.ru"
            ),
            Organization(
                code="org_002",
                name="АО 'ТехноПром'",
                address="г. Санкт-Петербург, Невский пр-т, д. 25",
                phone="+7 (812) 987-65-43",
                email="contact@technoprom.spb.ru"
            ),
            Organization(
                code="org_003",
                name="ИП Иванов И.И.",
                address="г. Екатеринбург, ул. Ленина, д. 5",
                phone="+7 (343) 555-44-33",
                email="ivanovii@mail.ru"
            )
        ]
        
        session.add_all(organizations)
        session.flush()  
        
        instructors = [
            Instructor(
                number="inst_001",
                full_name="Петров Александр Сергеевич",
                birth_date=date(1980, 5, 15),
                gender="мужской",
                education="МГТУ им. Баумана, факультет информатики",
                category=InstructorCategory.HIGHEST
            ),
            Instructor(
                number="inst_002",
                full_name="Смирнова Ольга Владимировна",
                birth_date=date(1975, 8, 22),
                gender="женский",
                education="МГУ, экономический факультет",
                category=InstructorCategory.FIRST
            ),
            Instructor(
                number="inst_003",
                full_name="Козлов Дмитрий Иванович",
                birth_date=date(1985, 3, 10),
                gender="мужской",
                education="СПбГУ, факультет менеджмента",
                category=InstructorCategory.SECOND
            )
        ]
        
        session.add_all(instructors)
        session.flush()
        
        courses = [
            Course(
                code="course_001",
                name="Основы программирования на Python",
                course_type=CourseType.IT,
                duration_days=5,
                max_students=15,
                organization_id=organizations[0].id
            ),
            Course(
                code="course_002",
                name="Управление проектами",
                course_type=CourseType.MANAGEMENT,
                duration_days=3,
                max_students=20,
                organization_id=organizations[1].id
            ),
            Course(
                code="course_003",
                name="Веб-разработка на Django",
                course_type=CourseType.IT,
                duration_days=7,
                max_students=12,
                organization_id=organizations[0].id
            )
        ]
        
        session.add_all(courses)
        session.flush()
        
        course_prices = [
            CoursePrice(
                course_id=courses[0].id,
                price=25000.0,
                document_number="Дог-001",
                document_date=date(2023, 1, 10),
                valid_from=date(2023, 1, 15),
                valid_to=date(2023, 12, 31)
            ),
            CoursePrice(
                course_id=courses[1].id,
                price=18000.0,
                document_number="Дог-002",
                document_date=date(2023, 2, 1),
                valid_from=date(2023, 2, 5),
                valid_to=None  # Текущая цена
            ),
            CoursePrice(
                course_id=courses[2].id,
                price=35000.0,
                document_number="Дог-003",
                document_date=date(2023, 3, 15),
                valid_from=date(2023, 3, 20),
                valid_to=date(2023, 6, 30)
            )
        ]
        
        session.add_all(course_prices)
        session.flush()
        
        assignment_documents = [
            AssignmentDocument(
                document_number="Назнач-001",
                document_date=date(2023, 4, 10),
                course_id=courses[0].id,
                instructor_id=instructors[0].id,
                start_date=date(2023, 4, 17),  
                end_date=date(2023, 4, 21)     
            ),
            AssignmentDocument(
                document_number="Назнач-002",
                document_date=date(2023, 5, 5),
                course_id=courses[1].id,
                instructor_id=instructors[1].id,
                start_date=date(2023, 5, 15),  
                end_date=date(2023, 5, 17)     
            )
        ]
        
        session.add_all(assignment_documents)
        session.flush()
        
        training_requests = [
            TrainingRequest(
                client_organization_id=organizations[2].id,
                course_id=courses[0].id,
                requested_start_date=date(2023, 6, 5),   
                requested_end_date=date(2023, 6, 9),     
                number_of_students=3,
                contact_phone="+7 (343) 555-44-33",
                contact_email="ivanovii@mail.ru",
                created_date=date(2023, 5, 20)
            ),
            TrainingRequest(
                client_organization_id=organizations[1].id,
                course_id=courses[1].id,
                requested_start_date=date(2023, 7, 10),  
                requested_end_date=date(2023, 7, 12),    
                number_of_students=5,
                contact_phone="+7 (812) 987-65-43",
                contact_email="contact@technoprom.spb.ru",
                created_date=date(2023, 6, 15)
            )
        ]
        
        session.add_all(training_requests)
        session.flush()
        
        students = [
            Student(
                training_request_id=training_requests[0].id,
                full_name="Иванов Петр Сергеевич",
                position="Разработчик"
            ),
            Student(
                training_request_id=training_requests[0].id,
                full_name="Сидорова Мария Ивановна",
                position="Тестировщик"
            ),
            Student(
                training_request_id=training_requests[0].id,
                full_name="Кузнецов Андрей Викторович",
                position="Аналитик"
            ),
            Student(
                training_request_id=training_requests[1].id,
                full_name="Николаев Дмитрий Олегович",
                position="Менеджер проектов"
            ),
            Student(
                training_request_id=training_requests[1].id,
                full_name="Федорова Елена Александровна",
                position="Координатор"
            )
        ]
        
        session.add_all(students)
        
        session.execute(course_instructor_association.insert().values([
            {'course_id': courses[0].id, 'instructor_id': instructors[0].id, 'assignment_document_id': assignment_documents[0].id},
            {'course_id': courses[1].id, 'instructor_id': instructors[1].id, 'assignment_document_id': assignment_documents[1].id},
            {'course_id': courses[2].id, 'instructor_id': instructors[2].id, 'assignment_document_id': None}
        ]))
        
        print("Тестовые данные успешно добавлены в базу данных!")

if __name__ == "__main__":
    create_test_data()