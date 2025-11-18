- File "C:\Users\Craig\AppData\Roaming\Python\Python314\site-packages\sqlalchemy\engine\default.py", line 951, in do_execute
    cursor.execute(statement, parameters)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: projects.short_description    
[SQL: SELECT projects.id AS projects_id, projects.client_id AS projects_client_id, projects.title AS projects_title, projects.slug AS projects_slug, projects.short_description AS projects_short_description, projects.description AS projects_description, projects.case_study AS projects_case_study, projects.tech_stack AS projects_tech_stack, projects.project_url AS projects_project_url, projects.date AS projects_date, projects.is_published AS projects_is_published, projects.is_featured AS projects_is_featured, projects.created_at AS projects_created_at, projects.updated_at AS projects_updated_at
FROM projects ORDER BY projects.date DESC
 LIMIT ? OFFSET ?]
[parameters: (100, 0)]
(Background on this error at: https://sqlalche.me/e/20/e3q8)