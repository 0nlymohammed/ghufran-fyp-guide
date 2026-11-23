CREATE TABLE students (
    id            SERIAL PRIMARY KEY,
    username      TEXT UNIQUE NOT NULL,
    full_name     TEXT NOT NULL,
    email         TEXT NOT NULL,
    major         TEXT NOT NULL,
    year          INT NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE grades (
    id         SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id),
    course     TEXT NOT NULL,
    grade      INT NOT NULL
);

CREATE TABLE sessions (
    token      TEXT PRIMARY KEY,
    student_id INT REFERENCES students(id),
    created_at TIMESTAMP DEFAULT now()
);

INSERT INTO students (username, full_name, email, major, year, password_hash) VALUES
  ('sara',   'Sara Ahmed',  'sara@campus.local',   'Computer Science',     4, encode(sha256('sara2026'::bytea), 'hex')),
  ('omar',   'Omar Khalid', 'omar@campus.local',   'Information Security', 3, encode(sha256('omar2026'::bytea), 'hex')),
  ('lina',   'Lina Hassan', 'lina@campus.local',   'Software Engineering', 2, encode(sha256('lina2026'::bytea), 'hex')),
  ('yousef', 'Yousef Ali',  'yousef@campus.local', 'Computer Networks',    4, encode(sha256('yousef2026'::bytea), 'hex'));

INSERT INTO grades (student_id, course, grade) VALUES
  (1, 'Network Security',  91),
  (1, 'Cloud Computing',   88),
  (2, 'Network Security',  58),
  (2, 'Databases',         64),
  (3, 'Network Security',  77),
  (3, 'Operating Systems', 82),
  (4, 'Network Security',  69),
  (4, 'Cloud Computing',   73);
