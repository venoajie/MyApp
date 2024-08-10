def greeting(details):
   match details:
      case [time, name]:
         return f'Good {time} {name}!'

print (greeting(["Morning", "Ravi"]))
print (greeting(["Afternoon","Guest"]))