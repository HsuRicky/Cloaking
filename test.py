from datetime import datetime

timestamp = 1702816932.5561473

date_time = datetime.fromtimestamp(timestamp)

year = date_time.year
month = date_time.month
day = date_time.day
hour = date_time.hour
minute = date_time.minute
second = date_time.second

print(f"{year}/{month}/{day} {hour}:{minute}:{second}")
 