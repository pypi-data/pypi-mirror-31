
# Inquirer.py
Inquirer.py is a collection of interactive Command Line Prompts inspired by [Inquirer.js](https://github.com/SBoudrias/Inquirer.js).



# Installation
Inquirer is can be installed via pip (PyPI). You have to just run the following command to install Inquirer

````bash

    pip install inquirer

````



# Usage
Inquirer is currently in development so it has only to types which are `input` and `confirm`.


## Input
**"type": "input"**

Example :-

````python

    from pythonInquirer import prompt

    question = [
        {
            "type": "input",
            "name": "username",
            "message": "Your Name"
        }
    ]

    answers = prompt(question)

````

## Confirm
**"type": "confirm"**

Example :-

````python

    from pythonInquirer import prompt

    question = [
        {
            "type": "confirm",
            "name": "confirm",
            "message": "Are You Sure"
        }
    ]

    answers = prompt(question)

````


# Answers Dictionary
The `prompt` function returns a dictionary of answers in which each questions `name` field is having that questions answers.

Example :-

````python

    from pythonInquirer import prompt

    question = [
        {
            "type": "input",
            "name": "username",
            "message": "Your Name"
        }
    ]

    answers = prompt(question)

    print("Username: " + answers["username"])

````