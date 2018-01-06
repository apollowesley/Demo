import csv

list = ['1', '2','3','4']
out = open(outfile, 'w')
csv_writer = csv.writer(out)
csv_writer.writerow(list)

# with open('example.csv', 'w', newline='') as f:
with open('some.csv', 'rb') as f:        # 采用b的方式处理可以省去很多问题
    #     reader = csv.reader(f, delimiter=':', quoting=csv.QUOTE_NONE)
    reader = csv.reader(f)
    for row in reader:
        print row


datas = [['name', 'age'],
         ['Bob', 14],
         ['Tom', 23],
        ['Jerry', '18']]        

with open('some.csv', 'wb') as f:      # 采用b的方式处理可以省去很多问题
    writer = csv.writer(f)
    writer.writerows(someiterable)       
   for row in datas:
        writer.writerow(row)


