from app import App

app = App()

items_to_analyze = app.get_list_of_items_to_analyze(False, 114562)

print("{} items para analise".format(str(len(items_to_analyze))))

i = 0

for item in items_to_analyze:
    report = app.timeline(item)
    if len(report) > 0:
        i += 1
        print(i)

