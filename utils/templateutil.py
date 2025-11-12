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


class SnakeMap():
    def __init__(self):
        # Settings
        self.width_of_text = 20
        self.horizontal_separator = "-"
        self.vertical_separator = "|"
        self.vertical_path_height = 3
    
    def __get_portions(self, length:int, value:int, reversed:bool=False) -> list:
        '''
        Examples:
        (4, 16) -> [4, 4, 4, 4]
        (5, 16) -> [4, 3, 3, 3, 3]
        (5, 16, True) -> [3, 3, 3, 3, 4]
        '''
        # Special cases
        if length == 0:
            return []
        # Algorithm
        result = [0 for _ in range(length)]
        addition = value // length
        for i in range(length):
            if i < value % length:
                result[i] += 1
            result[i] += addition
        if reversed:
            result.reverse()
        return result
    
    def __generate_vertical_path(self, width:int) -> str:
        vertical_path = ""
        for i in range(self.vertical_path_height):
            vertical_path += "\n" + " "*(width-len(self.vertical_separator)) + self.vertical_separator
        return vertical_path
    
    def __generate_row(self, chunk:list[str]) -> str:
        elems_length = sum(len(elem) for elem in chunk)
        total_gap_length = self.width_of_text-elems_length
        pattern = (" " + self.horizontal_separator)*self.width_of_text
        gaps_length_list = self.__get_portions(len(chunk)-1, total_gap_length)
        
        row = chunk[0]
        pos = 0
        for i, chunk_text in enumerate(chunk[1:]):
            gap_text = pattern[pos:(pos+gaps_length_list[i])]
            pos += gaps_length_list[i]
            row += gap_text + chunk_text
        return row
    
    def generate_map(self, list_of_elems:list[str], width:int) -> str:
        '''Generates snake like map using given list of elements'''
        #TODO if len(list_of_elems) % width == 1: UEB
        
        # Algorithm
        chunks = [list_of_elems[i:i + width] for i in range(0, len(list_of_elems), width)]
        
        # Reverse elements
        for i in range(len(chunks)):
            if i % 2 == 1:
                chunks[i].reverse()
        #rows = [horizontal_path.join(chunk) for chunk in chunks]
        rows = [self.__generate_row(chunk) for chunk in chunks]
        
        # Gathering result map
        result = "\n" + rows[0]
        for i, row in enumerate(rows[1:]):
            if i % 2 == 0:
                result += self.__generate_vertical_path( len(row) )
            else:
                result += self.__generate_vertical_path( 0 )
            result += "\n" + row
        return result

class VerticalMap():
    def __init__(self):
        self.sep = "-"
    
    def generate_map(self, list_of_elems:list) -> str:
        '''Generates vertical map using given list of elements'''
        result = "\n"
        for i, elem in enumerate(list_of_elems):
            result += self.sep + str(elem) + self.sep + "\n"
        return result

class HorizontalMap():
    def __init__(self):
        # Settings
        self.width_of_text = 40
        self.horizontal_separator = "-"
        self.margin = 2
    
    def __get_portions(self, length:int, value:int, reversed:bool=False) -> list:
        '''
        Examples:
        (4, 16) -> [4, 4, 4, 4]
        (5, 16) -> [4, 3, 3, 3, 3]
        (5, 16, True) -> [3, 3, 3, 3, 4]
        '''
        # Special cases
        if length == 0:
            return []
        # Algorithm
        result = [0 for _ in range(length)]
        addition = value // length
        for i in range(length):
            if i < value % length:
                result[i] += 1
            result[i] += addition
        if reversed:
            result.reverse()
        return result
    
    def __generate_row(self, chunk:list[str]) -> str:
        elems_length = sum(len(elem) for elem in chunk)
        total_gap_length = self.width_of_text-elems_length
        pattern = (" " + self.horizontal_separator)*self.width_of_text
        gaps_length_list = self.__get_portions(len(chunk)-1, total_gap_length)
        
        row = chunk[0]
        pos = 0
        for i, chunk_text in enumerate(chunk[1:]):
            gap_text = pattern[pos:(pos+gaps_length_list[i])]
            pos += gaps_length_list[i]
            row += gap_text + chunk_text
        return row
    
    def generate_map(self, list_of_elems:list[str], width:int) -> str:
        '''Generates snake like map using given list of elements'''
        #TODO if len(list_of_elems) % width == 1: UEB
        
        # Algorithm
        chunks = [list_of_elems[i:i + width] for i in range(0, len(list_of_elems), width)]
        rows = [self.__generate_row(chunk) for chunk in chunks]
        
        # Gathering result map
        result = ""
        for row in rows:
            result += row + "\n"*self.margin
        return result

horizontal_map = HorizontalMap()