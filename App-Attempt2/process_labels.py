import json

with open('assets/yamnet_class_map.csv') as f:
    lines = f.readlines()

foobar = lines[1:]

goober = []
for k in foobar:
    index, mid, display_name = k.split(',', maxsplit=2)
    goober.append(display_name.replace('"', '').replace('\n', ''))


wee = {'classes': goober, 'interested': [
    302, 303, 312, 325, 324,
    390, 317, 318, 319, 391,
    304, 392, 313, 450,
    195, 198, 321, 316
]}

print(json.dumps(wee, separators=(',', ':')))
