
class LoginData:

    def from_txt(path):
        
        with open(path, 'r') as file:
            data = file.read().splitlines()

        return data