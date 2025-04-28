-- Drop existing tables if they exist
DROP TABLE IF EXISTS flight_watchers;
DROP TABLE IF EXISTS flight;
DROP TABLE IF EXISTS user;

-- Users table
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

-- Flights table
-- TODO: Add "label" and "flyer" field
CREATE TABLE flight (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  airline TEXT NOT NULL,
  flight_number TEXT NOT NULL,
  flight_date DATE NOT NULL,
  departure_airport TEXT,
  arrival_airport TEXT,
  departure_time TIMESTAMP,
  arrival_time TIMESTAMP,
  status TEXT DEFAULT 'scheduled',
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_checked TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

