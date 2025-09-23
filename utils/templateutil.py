from functools import lru_cache

from jinja2 import Environment, FileSystemLoader, select_autoescape

from utils.config import settings


env = Environment(
    loader=FileSystemLoader(settings.template_dir),
    autoescape=select_autoescape()
)


@lru_cache
def get_template(template_name):
    return env.get_template(template_name)


def render(template_name, **kwargs):
    template = get_template(template_name)
    return template.render(**kwargs)


def elems_to_snake_map(list_of_elems:list, width:int) -> str:
    # Settings
    width_of_text = 20
    horizontal_separator = "-"
    vertical_separator = "|"
    vertical_path_height = 3
    
    # Preparations
    horizontal_path = horizontal_separator.join( [" " for i in range(4)] )
    def generate_vertical_path(width:int) -> str:
        vertical_path = ""
        for i in range(vertical_path_height):
            vertical_path += "\n" + " "*(width-len(vertical_separator)) + vertical_separator
        return vertical_path
    
    def generate_row(chunk:list[str]) -> str:
        elems_length = sum(len(elem) for elem in chunk)
        total_gap_length = width_of_text-elems_length
        pattern = (" " + horizontal_separator)*width_of_text
        one_gap_length = total_gap_length // (len(chunk)-1)
        last_gap_length = total_gap_length % (len(chunk)-1)
        
        row = chunk[0]
        for i, chunk_elem in enumerate(chunk[1:-1]):
            
            gapper = pattern[i*one_gap_length:(i+1)*one_gap_length]
            row += gapper + chunk_elem
        row += pattern[0:(one_gap_length + last_gap_length)] + chunk[-1]
        return row
    
    # Algorithm
    chunks = [list_of_elems[i:i + width] for i in range(0, len(list_of_elems), width)]
    
    # Reverse elements
    for i in range(len(chunks)):
        if i % 2 == 1:
            chunks[i].reverse()
    #rows = [horizontal_path.join(chunk) for chunk in chunks]
    rows = [generate_row(chunk) for chunk in chunks]
    
    # Gathering result map
    result = "\n" + rows[0]
    for i, row in enumerate(rows[1:]):
        if i % 2 == 0:
            result += generate_vertical_path( len(row) )
        else:
            result += generate_vertical_path( 0 )
        result += "\n" + row
    return result