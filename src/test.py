import yaml

with open('./config.yaml', 'r') as file:
    data = yaml.safe_load(file)

print(data['COMPANY']['TABLE_PATH'])