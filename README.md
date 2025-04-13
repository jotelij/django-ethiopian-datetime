# Ethiopian DateTime field for Django
Ethiopian datetime support for user interface. Easy conversion of DateTimeFiled to EthiopianDateTimeField within the admin site, view and templates.
The datetime data is stored in Gregorian calendar on database side and presented to the user as Ethiopian Calendar. Additionally UI interface is incorporated to the forms.

## Main Features
- Ethiopian calendar supported
- UI implemented admin site with templte
- Multiple languages: English, Amharic, Afan Oromo

## Usage 
Clone the package

    $ git clone https://github.com/jotelij/django-ethiopian-datetime
    $ cd django-ethiopian-datetime

Python virtual enviroment usage is recommended. Create a virtual enviroment in the folder and activate it. (Below is instruction for linux. Please use specific OS based command for creating and activating your own virtual enviroment)

    $ python3 -m venv venv
    $ . venv/bin/activate

Then you need to install required dependencies

    $ pip install -r requirements.txt


Then you are ready to go.

## Authors
- Jote Gutema