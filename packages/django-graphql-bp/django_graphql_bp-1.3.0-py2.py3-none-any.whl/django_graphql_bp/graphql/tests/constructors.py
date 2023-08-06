class Operation:
    type = None

    def __init__(self, name, output: dict, input: dict = None):
        self.name = name
        self.output = output
        self.input = input

    def get_input_result(self) -> str:
        result = ''

        if self.input is not None:
            input = self.get_clean_input()
            result += '(input: { \n'

            for field, value in input.items():
                if type(value) is str:
                    value = '"' + value + '"'
                elif type(value) is bool:
                    value = str(value).lower()
                elif type(value) is list:
                    value = str(value).replace('\'', '"')
                    import re
                    for match in re.findall('(?:{|, )(\".*?\"):', value):
                        replace = match.replace('"', '')
                        value = value.replace(match, replace)

                result += '    ' + field + ': ' + str(value) + '\n'

            result += '  })'

        return result

    def get_clean_input(self) -> {}:
        input = {}

        for field, value in self.input.items():
            if value is not None:
                input.update({field: value})

        return input

    def get_name(self) -> str:
        return self.name

    def get_output_result(self, output, spaces: int = 2) -> str:
        result = ' { \n'
        spaces_string = ' ' * spaces

        for field, value in output.items():
            if type(value) is dict:
                result += spaces_string + '  ' + field + self.get_output_result(value, spaces + 2)
            else:
                result += spaces_string + '  ' + field + '\n'

        result += spaces_string + '} \n'
        return result

    def get_result(self) -> str:
        result = self.type + ' ' + self.name + ' { \n'
        result += '  ' + self.name
        result += self.get_input_result()
        result += self.get_output_result(self.output)
        result += '}'
        return result


class Mutation(Operation):
    type = 'mutation'


class Query(Operation):
    type = 'query'
