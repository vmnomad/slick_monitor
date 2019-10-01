class Button(object):
    html = ""
    def get_html(self):
        return self.html

class Image(Button):
    def __init__(self,value):
        self.value = value
    html = "<img></img>"

class Input(Button):
    html = "<input></input>"

class Flash(Button):
   html = "<obj></obj>"

class ButtonFactory():
    def create_button(self, typ, test):
        targetclass = typ.capitalize()
        return globals()[targetclass](test)

button_obj = ButtonFactory()
button = ['image']
for b in button:
   print(dir(button_obj.create_button(b, 'hello')))