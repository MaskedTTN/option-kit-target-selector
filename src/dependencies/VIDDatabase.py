import sqlite3

from typing import Optional

class VIDDatabase:
    """Database for caching VIDs"""
    
    def __init__(self, db_path: str = 'vid_cache.db'):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Create database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vid_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vid TEXT UNIQUE NOT NULL,
            series TEXT NOT NULL,
            body TEXT,
            model TEXT,
            market TEXT,
            production_month TEXT,
            engine_code TEXT,
            steering TEXT,
            url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_series ON vid_cache(series)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_lookup ON vid_cache(series, model, market, body, steering, engine_code, production_month)')
        
        conn.commit()
        conn.close()
    
    def get_vid(self, series: str, body: str = None, model: str = None, 
            market: str = None, production: str = None, 
            engine: str = None, steering: str = None) -> Optional[dict]:
        """Get cached VID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM vid_cache WHERE series = ?"
        params = [series]

        if body:
            query += " AND body = ?"
            params.append(body)
        if model:
            query += " AND model = ?"
            params.append(model)
        if market:
            query += " AND market = ?"
            params.append(market)
        if production:
            query += " AND production_month = ?"
            params.append(production)
        if engine:
            query += " AND engine_code = ?"
            params.append(engine)
        if steering:
            query += " AND steering = ?"
            params.append(steering)
        
        query += " LIMIT 1"
        
        try:
            print(f"Executing query: {query}")
            print(f"With params: {params}")
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            print(f"Query result: {row}")

            if row:
                # Only access cursor.description if we got a row
                columns = [column[0] for column in cursor.description]
                result = dict(zip(columns, row))
                
                # Update last accessed
                cursor.execute(
                    'UPDATE vid_cache SET last_accessed = CURRENT_TIMESTAMP WHERE id = ?',
                    (row[0],)
                )
                conn.commit()
                conn.close()
                return result
            
            # No row found - return None without accessing cursor.description
            conn.close()
            return None
            
        except Exception as e:
            print(f"Error in get_vid: {e}")
            import traceback
            traceback.print_exc()
            conn.close()
            return None
    
    def save_vid(self, vid_data: dict):
        """Save VID to cache"""
        conn = sqlite3.connect(self.db_path)
        print(f"path: {self.db_path}")
        cursor = conn.cursor()

        try:
            print(f"Attempting to save VID: {vid_data}")
            
            # Check if VID already exists
            cursor.execute("SELECT vid FROM vid_cache WHERE vid = ?", (vid_data['vid'],))
            existing = cursor.fetchone()
            
            if existing:
                print(f"VID {vid_data['vid']} already exists in cache, skipping insert")
                conn.close()
                return
            
            # Insert new VID
            cursor.execute('''
            INSERT INTO vid_cache (
                vid, series, body, model, market,
                production_month, engine_code, steering, url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                vid_data['vid'],
                vid_data['series'],
                vid_data.get('body'),
                vid_data.get('model'),
                vid_data.get('market'),
                vid_data.get('production'),
                vid_data.get('engine'),
                vid_data.get('steering'),
                vid_data['url']
            ))
            
            conn.commit()
            print(f"Successfully saved VID: {vid_data['vid']}")
            
            # Verify it was saved
            cursor.execute("SELECT * FROM vid_cache WHERE vid = ?", (vid_data['vid'],))
            saved = cursor.fetchone()
            if saved:
                print(f"Verified VID in database: {saved}")
            else:
                print("WARNING: VID not found after insert!")
                
        except Exception as e:
            print(f"Error saving VID: {e}")
            import traceback
            traceback.print_exc()
        finally:
            conn.close()