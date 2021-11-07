# SET UP AND RUN APP
* Use MySQLWorkbench, execute the whole scripts: db_init.sql and then phase3_shell.sql (db_init.sql and phase3_shell.sql are under cs4400-phase > sql).  Please use phase3_shell.sql included in the indicated folder because it is updated with some more procedures than what we submitted for phase 3.
* Open app.py file (in cs4400-phase4 > src > app.py), update self.root_pw to your password to MySQLWorkbench
* Navigate to “cs4400-phase4 > src”

## From IDE (PyCharm, vscode)
* Run app.py
* (OPTIONAL) Include the “sys.path.append(‘[INSERT cs4400-phase4 PATH]’)” line in the app.py file

## From CMD/Terminal
* Run “python3 app.py”
* (OPTIONAL) Include the “‘[sys.path.append(INSERT cs4400-phase4 PATH])” line in the app.py file

# TECHNOLOGIES USED
## Platforms and IDEs
* PyCharm, Visual Studio Code, Sublime Text (to program the application)
* MySQLWorkbench (to host the database)

## Languages
* Python, SQL
* Required Python packages:
	* numpy           
	* pandas         
	* pip             
	* PyMySQL         
	* PyQt5           
	* PyQt5-sip       
	* PyQt5-stubs     
	* python-dateutil 
	* pytz            
	* setuptools      
	* six             

# PROCEDURE
* Split UI into different components: “Home Screens” and “Screens”
* Added “Utils” folder to include custom made classes
* Added .gitignore for removing unnecessary files
* Used Python’s PyQt5 library to create the UI all the screens
* Used pymysql to connect to the database

# WORK DISTRIBUTION
* Hymee Huang: UI and functionalities for screens 1, 2, 3s, 6, 14. 17
* Roy Gabriel: UI and functionalities for screens 4, 5, 12, 13,  15, 16
* Quynh Trinh: UI and functionalities for screens 7, 8, 9, 10, 11, 18
* All members cross-checked each other’s screens and tested the application together as a team

# NOTES
* For screen **Aggregate Result**, Date Processed follows this formatting:
	* Must include YYYY-MM-DD (i.e. 2020-10-10 or 2021-05-05 NOT 2020-5-5 or 20-20-10)
	* Incomplete dates are treated as NULL
* After a student signs up for a test and even though we only simulate tests (per the project description), student cannot see their pending test under the **Student View Test Results** screen until a lab technician add the new test to a pool. This is based on how the procedure 'student_view_results' was written (by a TA), so we assume this is the expected behavior of the system.
