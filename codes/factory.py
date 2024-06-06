from abc import abstractmethod, ABCMeta


# ----------------------
# Single Factory Pattern
# ----------------------
class Animal(metaclass=ABCMeta):
    @abstractmethod
    def do_say(self):
        raise NotImplementedError("Abstractclass method")


class Dog(Animal):
    def do_say(self):
        print("Bhow Bhow!!")


class Cat(Animal):
    def do_say(self):
        print("Meow Meow!!")


# Define forest factory
class ForestFactory:
    def make_sound(self, object_type):
        return eval(object_type)().do_say()


ff = ForestFactory()
ff.make_sound("Cat")

# ----------------------
# Factory Method Pattern
# ----------------------


class Section(metaclass=ABCMeta):
    @abstractmethod
    def describe(self):
        raise NotImplementedError("Abstractclass method")


# Concrete Product Class
class PersonalSection(Section):
    def describe(self):
        print("Personal Section")


class AlbumSection(Section):
    def describe(self):
        print("Album Section")


class PatentSection(Section):
    def describe(self):
        print("Patent Section")


class PublicationSection(Section):
    def describe(self):
        print("Publication Section")


# Creator Abstract Class: provide factory method
class Profile(metaclass=ABCMeta):
    def __init__(self):
        print(f"Create profile... {type(self).__name__}")
        self.sections = []
        self.create_profile()

    @abstractmethod
    def create_profile(self):  # factory method
        raise NotImplementedError("Abstractclass method")

    def get_sections(self):
        return self.sections

    def add_section(self, section: Section):
        self.sections.append(section)


# Concrete Creator Class
class Linkdin(Profile):
    def create_profile(self):
        self.add_section(PersonalSection())
        self.add_section(PatentSection())
        self.add_section(PublicationSection())


class Facebook(Profile):
    def create_profile(self):
        self.add_section(PersonalSection())
        self.add_section(AlbumSection())


profile = Linkdin()
