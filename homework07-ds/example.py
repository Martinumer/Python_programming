import psycopg2
import psycopg2.extras
from pprint import pprint as pp
from tabulate import tabulate


c = psycopg2.connect("host=localhost port=5432 dbname=odscourse user=postgres password=secret")
curs = c.cursor()

def fetch_all(curs):
    colnames = [desc[0] for desc in curs.description]
    records = curs.fetchall()
    return [{colname: value for colname, value in zip(colnames, record)} for record in records]


curs.execute("SELECT * FROM adult_data LIMIT 5")
records = curs.fetchall()
print("First 5 lines:")
print(tabulate(records))

#1. Сколько мужчин и женщин (признак sex) представлено в этом наборе данных?
curs.execute(
    """
    SELECT sex, COUNT(*)
        FROM adult_data
        GROUP BY sex
    """
)
print("Amount of men and women:")
print(tabulate(fetch_all(curs), "keys", "psql"))

#2. Каков средний возраст (признак age) женщин?

curs.execute("""
    SELECT AVG(age) FROM adult_data WHERE sex = 'Female'
""")
print("Average women age:")
print(tabulate(fetch_all(curs), "keys", "psql"))

#3. Какова доля граждан Германии (признак native-country)?

curs.execute( """
    SELECT native_country, ROUND((COUNT(*) / (SELECT COUNT(*) FROM adult_data)::numeric), 6)
        FROM adult_data WHERE native_country = 'Germany'
        GROUP BY native_country;
    """
)
print("Share of Germans:")
print(tabulate(fetch_all(curs), "keys", "psql"))

#4-5. Каковы средние значения и среднеквадратичные отклонения возраста тех, кто получает более 50K в год (признак *salary) и тех, кто получает менее 50K в год?

curs.execute("""
    SELECT AVG(age), STDDEV(age) FROM adult_data WHERE salary = '>50K'
""")
print("Average age and std deviation for >50K:")
print(tabulate(fetch_all(curs), "keys", "psql"))


curs.execute("""
    SELECT AVG(age), STDDEV(age) FROM adult_data WHERE salary = '<=50K'
""")
print("Average age and std deviation for <=50K:")
print(tabulate(fetch_all(curs), "keys", "psql"))

#6. Правда ли, что люди, которые получают больше 50k, имеют как минимум высшее образование? (признак education – Bachelors, Prof-school, Assoc-acdm, Assoc-voc, Masters или Doctorate)

curs.execute("""
    SELECT education, salary FROM adult_data WHERE salary = '>50K'
    GROUP BY education, salary
""")
print("Education of rich people:")
print(tabulate(fetch_all(curs), "keys", "psql"))

#7. Выведите статистику возраста для каждой расы (признак race) и каждого пола. Используйте groupby и describe. Найдите таким образом максимальный возраст мужчин расы Amer-Indian-Eskimo.

curs.execute("""
    SELECT COUNT(*),
           AVG(age), STDDEV(age), MIN(age), MAX(age), sex, race
    FROM adult_data
    GROUP BY race, sex
""")
print("Age statistics:")
print(tabulate(fetch_all(curs), "keys", "psql"))

curs.execute("""
    SELECT MAX(age)
    FROM adult_data WHERE sex = 'Male' AND race = 'Amer-Indian-Eskimo'
    GROUP BY race
""")
print("Max age of male Amer-Indian-Eskimo:")
print(tabulate(fetch_all(curs), "keys", "psql"))

#8. Среди кого больше доля зарабатывающих много (>50K): среди женатых или холостых мужчин (признак marital-status)? Женатыми считаем тех, у кого marital-status начинается с Married (Married-civ-spouse, Married-spouse-absent или Married-AF-spouse), остальных считаем холостыми.

curs.execute("""
    SELECT ROUND((COUNT(*) / (SELECT COUNT(*) FROM adult_data)::numeric), 6), salary, marital_status
    FROM adult_data WHERE salary = '>50K'
    GROUP BY marital_status, salary
            """)
print("Impact of marital status:")
print(tabulate(fetch_all(curs), "keys", "psql"))

#9. Какое максимальное число часов человек работает в неделю (признак hours-per-week)? Сколько людей работают такое количество часов и каков среди них процент зарабатывающих много?

curs.execute("SELECT MAX(hours_per_week::int) FROM adult_data")
print("Max hours-per-week:")
print(tabulate(fetch_all(curs), "keys", "psql"))

curs.execute(
    """
    SELECT COUNT(*)
        FROM adult_data WHERE hours_per_week = 99
    """
)
print("Amount of people working max hours-per-week:")
print(tabulate(fetch_all(curs), "keys", "psql"))

curs.execute("""
    SELECT COUNT(*)
    FROM adult_data
    WHERE hours_per_week = '99' AND salary = '>50K'
    GROUP BY hours_per_week;
""")

high_salary = fetch_all(curs)[0]['count']

curs.execute("""
    SELECT COUNT(*)
    FROM adult_data
    WHERE hours_per_week = '99'
    GROUP BY hours_per_week;
""")

all = fetch_all(curs)[0]['count']
print("Percentage of rich and hard-working:", round(high_salary / all * 100), '%')

#10. Посчитайте среднее время работы (hours-per-week) зарабатывающих мало и много (salary) для каждой страны (native-country).

curs.execute(
    """
    SELECT native_country, salary, ROUND(AVG(hours_per_week))
    FROM adult_data
    GROUP BY native_country, salary
    """)

# Среднее время работы для зарабатывающих мало и много в каждой стране
print("Average hours-per-week for every country:")
print(tabulate(fetch_all(curs), "keys", "psql"))
