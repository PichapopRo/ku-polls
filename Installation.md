## Installation guide
1. Clone directory
```
git clone https://github.com/PichapopRo/ku-polls.git
```
2. Change directory
```
cd ku-polls
```
3. Install a Virtual Environment
```
python -m venv .venv
```
4. Activate a Virtual Environment
```
.venv\Scripts\Activate
```
5. Installing requirement
```
pip install -r requirements.txt
```
6. Migrate
```
python manage.py migrate
```
7. Load data
```
python manage.py loaddata data/users.json
python manage.py loaddata data/polls-v4.json
python manage.py loaddata data/votes-v4.json
```
8. Runserver
```
python manage.py runserver
```