import sys

def main(bname):
    if '_' in bname:
        class_name = [x.capitalize() for x in bname.split('_')]
    else:
        class_name = [bname.capitalize()]
    class_name.append('Driver')
    class_name = ''.join(class_name)

    with open('.templates/driver.py', 'r') as file:
        content = file.read()
    
    content = content.replace('CustomDriver()', f'{class_name}()')
    with open(f'.templates/{bname}_driver.py', 'w') as file:
        file.write(content)
    
    with open(f'.templates/__init__.py', 'w') as file:
        file.write(f'from .{bname}_driver import {class_name}')
    
    with open(f'.templates/README.md', 'w') as file:
        file.write(f'# {class_name[:-6]}')

if __name__ == "__main__":
    # Check if exactly one argument is passed
    if len(sys.argv) != 2:
        print("Usage: python3 customize.py benchmark_name")
    else:
        # Pass the argument to the main function
        bname = sys.argv[1]
        main(bname)
