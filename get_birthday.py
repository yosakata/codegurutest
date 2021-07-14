import sys
import string 
from datetime import date 
from datetime import datetime
import re 

def get_age_today(birthday):
    m = re.search(r'(\d+)/(\d+)/(\d+)', birthday)
    birth_year = int(m.group(1))
    birth_month = int(m.group(2))
    birth_day = int(m.group(3))

    today = date.today()
    # before birthday
    if (today.month, today.day) < (birth_month, birth_day):
        return today.year - birth_year - 1
    else:
        return today.year - birth_year

rere


def main():
    birthday = sys.argv[1]
    print(get_age_today(birthday)) 

if __name__ == "__main__":
    main()
