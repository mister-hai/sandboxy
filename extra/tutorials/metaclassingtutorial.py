
################################################################################
##############            METACLASSING TUTORIAL                #################
# https://www.programiz.com/python-programming/multiple-inheritance            #
# https://www.programiz.com/python-programming/multiple-inheritance            #
################################################################################

# so you can have your base class just sitting there being itself, right?
class ClassA():
    def __init__(self, message):
        print(message)

# when another class comes along...
class DecoratorFactory():
    """
    An example of how to dynamically create classes based on params

    Args:
        codeobject (object): An arbitrary function or bit of code as a single object
    """
    # and when it starts operation, its telling the other class to do something!
    # "codeobject" can be literally anything, but its most effective if you use
    # a class or a function, this is the basis of decorators which will be shown 
    # further below
    def __init__(self, codeobject):
        print("ClassB.__init__()")
        self.codeobject = codeobject
        self.codeobject()

# using the classes
message = "this message is piped through the scope to an arbitrary class"
testinstance = Dog(ClassA,message=message)
testinstance

# but then you have this other class here, it unpacks arguments into itself
class Prototype1():
    """
    The Class Accepts a dict, it turns those key,value pairs into 
    class attributes in the form of 
    >>> dictofmany = {'integer':42069,'string':'ayyyyy lmao'}
    >>> test = Prototype1(**dictofmany)
    >>> test.integer
    42069
    >>> test.string
    ayyyyy lmao

    """
    # __cls__ is the "dunder" method for "inherent trait to the class"
    # cls attributes are like saying
    # Dog.Family = "canidae"
    # dog.species = "Canis lupus familiaris"
    # Dog.name   = "poopmaster9001"

    # in this example, a dogs name.... is something that is not inherent to that animal itself
    # however, its species and taxonomic nomenclature ARE inherent values, assigned to ALL dogs
    
    # you would assign those values here, in the __cls__ "dunder" method

    # ** "unpacks" the dict
    # https://realpython.com/python-kwargs-and-args/
    def __init__(self,**entries):
        self.__dict__.update(entries)

# this inherits from Prototype1
class Prototype2(Prototype1):
    def __init__(self,**entries):
        super().__init__(**entries)

# a further abstraction, using dicts as "payloads"
# this ends up assigning a function pointer to ClassB(ClassA,message=message)   
# on to the Prototype1 Class as the attribute "dog"
protopayload = {"dog": Dog}
qwer = Prototype2(**protopayload)
# dog go bork bork
message = "BORK BORK I POOP ON U"
qwer.dog(ClassA,message=message)

# what if you want a better dog factory?
class ProtoClass(Dog):
    '''
    Prototype base class , set name with "name = str".
    '''
    def __init__(self,*args, **kwargs):
        self.__name__ = kwargs.pop('name')
        self.__qualname__= self.__name__
        return super().__init__(**kwargs)

#Wanna see something neat?
dog = {"name": "Dog", "type": "corgie", "cutefactor": 5, "nickname":"fuzzbutt"}
newdogsohappy = ProtoClass(**dog)

# this will be explored further below
# https://stackoverflow.com/questions/1639174/creating-class-instance-properties-from-a-dictionary
print(type(newdogsohappy))

dictofmany = {
    "name": "UtterNonsense",
    'integer':42069,
    'string':'ayyyyy lmao',
    # this is called "assigning a function pointer" in other languages
    # this function runs when you call this attribute/key
    'function': print("aren't I so funny?"),
    # you can end with a trailing comma
    # this line ends up assigning nothing to nothing, a moot point
    None : None,
}

# Demonstration of MRO
#https://www.programiz.com/python-programming/multiple-inheritance
class X:
    pass


class Y:
    pass


class Z:
    pass


class A(X, Y):
    pass


class B(Y, Z):
    pass


class M(B, A, Z):
    pass

# Output:
# [<class '__main__.M'>, <class '__main__.B'>,
#  <class '__main__.A'>, <class '__main__.X'>,
#  <class '__main__.Y'>, <class '__main__.Z'>,
#  <class 'object'>]

print(M.mro())

# program to create class dynamically
# this method sets "class attributes" e.g. "cls"
  
# https://www.geeksforgeeks.org/create-classes-dynamically-in-python/
class classfactory():
    def __init__(self):
        pass
    # constructor
    def constructor(self, arg):
        self.constructor_arg = arg
  
    # define functions to add to the class you want to create
    # method
    def displayMethod(self, arg):
        print(arg)
  
    # class method
    @classmethod
    def classMethod(cls, arg):
        print(arg)
  
    # creating class dynamically
    Geeks = type("Geeks", (object, ), {
        # constructor
        "__init__": constructor,
      
        # data members
        "string_attribute": "Geeks 4 geeks !",
        "int_attribute": 1706256,
      
        # member functions
        "func_arg": displayMethod,
        "class_func": classMethod
    })
  
    # creating objects
    
    obj = Geeks("constructor argument")
    print(obj.constructor_arg)
    print(obj.string_attribute)
    print(obj.int_attribute)
    obj.func_arg("Geeks for Geeks")
    Geeks.class_func("Class Dynamically Created !")