class BooleanConverter:
    regex = '(True|False)'
    
    def to_python(self, value):
        return value == "True"

    def to_url(self, value):
        return str(value)
