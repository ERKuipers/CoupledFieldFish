import configparser

def generate_config_file():
    config = configparser.ConfigParser()
    
    # Add sections and options with values
    config['General'] = {'key1': 'value1', 'key2': 'value2'}
    config['Database'] = {'host': 'localhost', 'port': '3306', 'user': 'user', 'password': 'password'}
    
    # Add comments to options
    config['General']['key1'] = '# This is a comment for key1'
    
    # Write the configuration to a file
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# Generate the configuration file
generate_config_file()