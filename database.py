import sqlite3
from datetime import datetime
import json
import logging

class Database:
    def __init__(self, db_file="csv_manager.db"):
        self.db_file = db_file
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_file)

    def init_database(self):
        """Initialize the database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                row_count INTEGER
            )
        """)
        
        # Create file_data table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_data (
            data_id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER,
            row_data TEXT NOT NULL,
            column_names TEXT NOT NULL,
            FOREIGN KEY (file_id) REFERENCES files (file_id)
        )
        ''')

        # Drop existing crawled_data table if it exists
        cursor.execute('DROP TABLE IF EXISTS crawled_data')
        
        # Create crawled_data table with correct schema
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS crawled_data (
            crawl_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            crunchbase_url TEXT,
            html_content TEXT,
            crawl_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'success',
            error TEXT,
            source_file_id INTEGER,
            FOREIGN KEY (source_file_id) REFERENCES files (file_id)
        )
        ''')

        # Create company_profiles table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_profiles (
            profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            profile_text TEXT,
            source_file_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT,
            FOREIGN KEY (source_file_id) REFERENCES files (file_id)
        )
        ''')
        
        conn.commit()
        conn.close()

    def add_file(self, filename, file_type):
        """Add a new file record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO files (filename, file_type, created_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (filename, file_type))
        
        file_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return file_id

    def add_file_data(self, file_id, row_data, column_names):
        """Add data from a file"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO file_data (file_id, row_data, column_names)
        VALUES (?, ?, ?)
        ''', (file_id, row_data, column_names))
        
        conn.commit()
        conn.close()

    def update_row_count(self, file_id, count):
        """Update the row count for a file"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE files 
        SET row_count = ?
        WHERE file_id = ?
        ''', (count, file_id))
        
        conn.commit()
        conn.close()

    def get_all_files(self):
        """Get list of all files"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT file_id, filename, file_type, created_at, row_count 
        FROM files 
        ORDER BY created_at DESC
        ''')
        
        files = cursor.fetchall()
        conn.close()
        return files

    def get_file_data(self, file_id):
        """Get all data rows for a specific file"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # First check if the file exists
            cursor.execute('SELECT file_id FROM files WHERE file_id = ?', (file_id,))
            if not cursor.fetchone():
                print(f"No file found with ID: {file_id}")
                return None

            # Get the file data
            cursor.execute('''
                SELECT row_data, column_names 
                FROM file_data 
                WHERE file_id = ?
                ORDER BY data_id
            ''', (file_id,))
            
            data = cursor.fetchall()
            if not data:
                print(f"No data rows found for file ID: {file_id}")
            return data
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()

    def delete_file(self, file_id):
        """Delete a file and its data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM file_data WHERE file_id = ?', (file_id,))
        cursor.execute('DELETE FROM files WHERE file_id = ?', (file_id,))
        
        conn.commit()
        conn.close()

    def save_crawled_data(self, company_name, url, html_content, source_file_id, status='success', error_message=None):
        """Save crawled data to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO crawled_data 
                (company_name, crunchbase_url, html_content, source_file_id, status, error)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (company_name, url, html_content, source_file_id, status, error_message))
            
            crawl_id = cursor.lastrowid
            conn.commit()
            return crawl_id
        except sqlite3.Error as e:
            logging.error(f"Database error in save_crawled_data: {e}")
            return None
        finally:
            conn.close()

    def get_crawled_data(self, source_file_id=None, url=None):
        """Retrieve crawled data from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if url:
                cursor.execute('''
                    SELECT crawl_id, company_name, crunchbase_url, html_content, crawl_date, status, error
                    FROM crawled_data
                    WHERE crunchbase_url = ?
                ''', (url,))
            elif source_file_id:
                cursor.execute('''
                    SELECT crawl_id, company_name, crunchbase_url, html_content, crawl_date, status, error
                    FROM crawled_data
                    WHERE source_file_id = ?
                ''', (source_file_id,))
            else:
                cursor.execute('''
                    SELECT crawl_id, company_name, crunchbase_url, html_content, crawl_date, status, error
                    FROM crawled_data
                ''')
            
            data = cursor.fetchall()
            logging.info(f"Retrieved {len(data)} records from crawled_data")
            return data
            
        except sqlite3.Error as e:
            logging.error(f"Database error in get_crawled_data: {e}")
            return None
        finally:
            conn.close()

    def get_company_details_by_file(self, file_id):
        """Get company details and related crawled data for a specific file"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # First get all file data to extract company details
            cursor.execute('''
                SELECT row_data
                FROM file_data
                WHERE file_id = ?
            ''', (file_id,))
            
            file_data = cursor.fetchall()
            companies = []
            
            for row in file_data:
                try:
                    row_dict = json.loads(row[0])
                    company_info = {
                        'company_name': row_dict.get('Company Name', ''),
                        'funded_date': row_dict.get('Funded Date', '')
                    }
                    
                    # Get related crawled data
                    cursor.execute('''
                        SELECT html_content
                        FROM crawled_data
                        WHERE company_name = ? AND source_file_id = ?
                    ''', (company_info['company_name'], file_id))
                    
                    crawled_data = cursor.fetchone()
                    if crawled_data:
                        company_info['html_content'] = crawled_data[0]
                    else:
                        company_info['html_content'] = None
                    
                    companies.append(company_info)
                except json.JSONDecodeError:
                    continue
            
            return companies
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()

    def save_company_profile(self, data):
        """Save generated cold email to database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO company_profiles 
                (company_name, profile_text, source_file_id, created_at, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                data['company_name'],
                data['profile_text'],
                data['source_file_id'],
                datetime.now().isoformat(),
                data['status']
            ))
            
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error saving company profile: {str(e)}")
            return False
        finally:
            conn.close()

    def get_company_profiles(self, file_id: int):
        """Get all company profiles for a file"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT company_name, profile_text
                FROM company_profiles
                WHERE source_file_id = ?
            """, (file_id,))
            rows = cursor.fetchall()
            if not rows:
                logging.warning(f"No company profiles found for file_id: {file_id}")
                return []
                
            profiles = []
            for row in rows:
                profiles.append({
                    'company_name': row[0],
                    'profile_text': row[1]
                })
            
            logging.info(f"Found {len(profiles)} company profiles for file_id: {file_id}")
            return profiles
            
        except Exception as e:
            logging.error(f"Error getting company profiles: {str(e)}")
            return []
        finally:
            conn.close()

    def get_all_company_profiles(self):
        """Get all company profiles from the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT profile_id, company_name, profile_text, created_at, status
                FROM company_profiles
                WHERE status = 'success'
                ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            profiles = []
            
            for row in rows:
                profile = {
                    'profile_id': row[0],
                    'company_name': row[1],
                    'profile_text': row[2],
                    'created_at': row[3],
                    'status': row[4]
                }
                profiles.append(profile)
            
            logging.info(f"Retrieved {len(profiles)} company profiles")
            return profiles
            
        except Exception as e:
            logging.error(f"Error getting all company profiles: {str(e)}")
            return []
        finally:
            conn.close()

    def get_file_by_id(self, file_id: int) -> dict:
        """Get file data by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT file_id, filename, file_type, created_at, row_count 
                FROM files 
                WHERE file_id = ?
            """, (file_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
                
            return {
                'id': row[0],
                'filename': row[1],
                'file_type': row[2],
                'created_at': row[3],
                'row_count': row[4]
            }
        except Exception as e:
            logging.error(f"Error getting file by ID: {str(e)}")
            return None
        finally:
            conn.close()

    def get_all_files(self):
        """Get all files with their details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT file_id, filename, file_type, row_count, created_at
            FROM files
            ORDER BY created_at DESC
        """)
        return cursor.fetchall()

    def get_file_details(self, file_id: int) -> tuple:
        """Get file details by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT file_id, filename, file_type, created_at, row_count
                FROM files
                WHERE file_id = ?
            """, (file_id,))
            
            row = cursor.fetchone()
            if not row:
                logging.warning(f"No file found with ID: {file_id}")
                return None
                
            return row
            
        except Exception as e:
            logging.error(f"Error getting file details: {str(e)}")
            return None
        finally:
            conn.close()

    def empty_tables(self):
        """Empty all tables in the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # List of tables to empty
            tables = [
                'files',
                'file_data',
                'crawled_data',
                'company_profiles'
            ]
            
            # Empty each table
            for table in tables:
                cursor.execute(f"DELETE FROM {table}")
            
            # Reset auto-increment counters
            for table in tables:
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
            
            conn.commit()
            cursor.close()
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error emptying tables: {str(e)}")
        finally:
            conn.close()
