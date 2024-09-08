## KU Polls: Online Survey Questions 

An application to conduct online polls and surveys based
on the [Django Tutorial project](https://docs.djangoproject.com/en/5.1/intro/tutorial01/), with
additional features.

This app was created as part of the [Individual Software Process](
https://cpske.github.io/ISP) course at [Kasetsart University](https://www.ku.ac.th).

## Installation

1. Clone directory
```
git clone https://github.com/PichapopRo/ku-polls.git 
```
2. Change directory to ku-polls
```
cd ku-polls
```
3. Install requirements
```
pip install -r requirements.txt
```


## Running the Application
1. Migrate
```
python manage.py migrate
```
2. Load data
```
python manage.py loaddata data/polls-v3.json
python manage.py loaddata data/users.json
```
3. Runserver
```
python manage.py runserver
```

## Project Documents

All project documents are in the [Project Wiki](../../wiki/Home).


- [Vision Statement](../../ku-polls/wiki/Vision-and-Scope)
- [Requirements](../../ku-polls/wiki/Requirements)
- [Project Plan](../../ku-polls/wiki/Project-Plan)
- [Domain Model Diagram](../../ku-polls/wiki/Domain-Model-Diagram)
- [Iteration 1 Plan](../../ku-polls/wiki/Iteration-1-Plan)
- [Iteration 2 Plan](../../ku-polls/wiki/iteration-2-Plan)
- [Iteration 3 Plan](../../ku-polls/wiki/Iteration-3-Plan)
