# DonationLib

**Connects donated books from donator to donatee**!

### Objectives
This project aims to improve and simplify the donation process for books by connecting those with books ready to donate with those looking for the same book. In completing this goal, it should protect user security and privacy and remain completely free to use and accessible.

### Implementation Details and Architecture
The project consists of 2 main programs -- a Flask API and a *Beeware* front-end. 

The Flask API is hosted on *Railway* and accepts API requests from the front-end application. It utilizes Flask-SQLAlchemy to provide ORM to create various endpoints with Flask that interact with a remotely-hosted *PostgreSQL* database. To ensure security, the API also uses `argon2` and doesn't store raw passwords, instead utilizing password hashes. 

The *Beeware* front-end uses *Beeware's Toga* for creating the user interface with *Beeware's Briefcase* used for packaging and distribution. The program interacts with the API using the requests module. It also uses json and pathlib for data management.

### Attribution
The aforementioned modules and its dependencies are used for both programs. A full list of all python modules used is available in `requirements.txt`. User interfaces were created with Toga, and the only media externally sourced are the icons (see `bookcharityapp/src/bookcharityapp/res/icons/README.md` for attribution details).

### AI Disclosures
Artificial Intelligence and Generative AI were used in a few, very limited ways in the project.

One use case for it was research, e.g. to help extrapolate information from documentation or to generate example code to explain features and typical implementations (this code was not used in the project, it was only used for learning)

Another use case was *Github Copilot*, which was unknowingly used in development for a very limited time. Importantly though, it simply increased typing speed as I would have implemented all the code in exactly the same way.

Finally, AI was sometimes used to help with debugging if I couldn't solve the issue on my own e.g. explaining difficult tracebacks or misleading error messages to iterate faster and simplify debugging and environment configuration

Note: AI was **NOT** used to generate any media and **NO** *vibe coding* was used in the project. Additionally, any AI-generated code used was written exactly as I intended to implement it (and I wasn't aware it was AI until after using it for ~3 hrs, at which point it was disabled).