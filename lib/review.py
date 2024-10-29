from __init__ import CURSOR, CONN
from department import Department
from employee import Employee

class Review:
    
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?);
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        self.id = CURSOR.lastrowid  # Get the primary key of the new row
        Review.all[self.id] = self  # Save the instance in the dictionary
        CONN.commit()
    
    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, employee_id):
        if not self._employee_exists(employee_id):
            raise ValueError("Employee ID does not exist in the database.")
        self._employee_id = employee_id

    @classmethod
    def _employee_exists(cls, employee_id):
        """Check if an employee exists in the database."""
        sql = "SELECT id FROM employees WHERE id = ?;"
        CURSOR.execute(sql, (employee_id,))
        return CURSOR.fetchone() is not None

    @classmethod
    def create(cls, year, summary, employee_id):
        """Initialize a new Review instance and save the object to the database."""
        if not isinstance(year, int):
            raise ValueError("Year must be an integer.")
        if year < 2000:
            raise ValueError("Year must be greater than or equal to 2000.")
        if not summary or not isinstance(summary, str):
            raise ValueError("Summary must be a non-empty string.")
        
        review = cls(year, summary, employee_id)
        review.save()  # Ensure this method is correctly implemented to save to the database
        return review

    @classmethod
    def instance_from_db(cls, row):
        return cls(id=row[0], year=row[1], summary=row[2], employee_id=row[3])

    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM reviews WHERE id = ?;"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self):
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?;
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        sql = "DELETE FROM reviews WHERE id = ?;"
        CURSOR.execute(sql, (self.id,))
        del Review.all[self.id]  # Remove from the local dictionary
        self.id = None  # Reset the id attribute
        CONN.commit()

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM reviews;"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]
