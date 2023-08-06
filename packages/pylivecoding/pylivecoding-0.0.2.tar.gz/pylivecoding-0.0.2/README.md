
# pylivecoding
Pylivecoding is a live coding environment implementation inspired by Smalltalk

Essentially this library reloads modules and updates all live instances of classes defined in those modules to the latest code of the class definition without losing any of the data/state. This way you can change code in your favorite code editor and IDE and immediately see the results without any delays afer you save the module. 

# How to use
First please not that this library needs CPython 3.5 and above. It won't work with Python 2. 

Pylivecoding is an extremely small library and its functionality is super simple. 
First of course you import the single module pylovecoding.py to your project. 
```python
import livecoding
```
if the folder that contains your main module that will reload the other modules is \_\_init\_\_.py then the import must be
```py
from . import livecoding
```
if it is a subpackage then the import must be
```py
from .. import livecoding
```
Then you need to initialize the live coding enviroment and add to it the modules which will have their code be reloaded
```py
live_env = livecoding.LiveEnviroment()
live_env.live_modules = ['myproject.module1', 'myproject.module2', 'myproject.module3']
live_env.update()
```
Cyclops in this case is the name of our project in case you use it as a python package. So you must replace ```package``` witht the name of your package and ```module1``` etc with the name of your module. A package means its a folder that containes \_\_init\_\_.py if you dont use python packages then it should look like this
```py
live_env = livecoding.LiveEnviroment()
live_env.live_modules = [module1', 'module2', 'module3']
live_env.update()
```
In order for your modules to be reloaded and the live instances to be updated you have to issue the update command
```python
livecoding.update_env()
```
This should be coded in a module that won't be used for live coding. Also the update and general live coding makes sense for code that repeats so its better put this update inside a loop of some sort. 
 
Your modules can be any kind of Python modules as long as all live classes are subclasses of livecoding.LiveObject.
```python
import livecoding

class MyClass(livecoding.LiveObject):
```
If you dont want to subclass LiveObject then all you have to do is take a look at that class and try to add similar functionality to your class. Which means your class must have a class variable called ```instances``` and that each time an instance is created that instance is added to that variable. For example
```py
class MyLiveObjectClass:
    instances=[]

    def __init__(self):
            self.__class__.instances.append(self)

```
Thats all you have to do and you can code as you awlays code following whatever style you want. 
# Debugging live coding 
Traditional debugging compared to live code debugging is like fire compared to nucleal power. Because not only you see the problems in your source code you can also change the live code while still the debugger is stepping through your code. This allows coding Smalltalk style. In Smalltalk some coders code entirely inside the debugger, they make intentional mistakes under the safety that they can correct their errors with no delays at all because there is no need to restart the debugger and each new error triggers the debugger again.When the error is fixed via live coding, the breakpoint can be removed and the debugger instructed to continue execution like nothing happened. 
 
Fortunately python does provide such functionality through the use of post mortem debugging. Essentially it means that in the case of error the debugger triggers using the line that triggered the error as a temporary breakpoint. The code is the following
 
```python
try:
  live_env.update()
  execute_my_code()
except Exception as inst:
  
  type, value, tb = sys.exc_info()
  traceback.print_exc()
  pdb.post_mortem(tb)
```
 
As you can see we have here a usual python exception handling code, inside the try we first live update our code to make sure it updated to the latest source code and execute our code , if an error occur or anyting else, it is stored and printed and then the debugger is triggered , hitting c inside pdb will continue execution with the first statement being updating to live code. 
 
The assumption here is that all this runs inside a loop of some sort so you can actually see the results of the updated code. Obviously if it is not and this is the last line of code , the application will just end  end execution after the debugger was instructed to continue with the "c" command ;) 

# The actual benefits of live coding
Technically speaking you can even use your source code editor as a debugger the reason being because of live coding you can print real time whatever value you want, inspect and even modify existing objects and generally do all the things you want even create your own breakpoints using if conditions that will stop the execution if specific criteria are met. Also you wont have the bigest disadvantage of a debugger , its inability to change the source code. 

Obviously this works great with Test Driven Development because the ability to lively manipulate tests maks writting tests far easier. Live coding empowers the users with the ease needed to constantly experiment with code and it makes the whole experience far more enjoyable and productive.

live coding make REPLs also uneccessary for the same reason. Through live coding, your source code turns to essentially a REPL on steroids.

# Future plans
The library is far from finished. The Smalltalk enviroment comes with a wealth of conveniences and automations and a very powerful IDE. Generally Python is powerful enough to do those things and there are good enough IDEs out there but I will be replicating some of the ideas to make my life easier. So to do list is the following
 
 - Make the library smart enough to detect changes inside modules and automatically update the live code/state
 
