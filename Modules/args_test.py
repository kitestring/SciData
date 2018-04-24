def test_var_args(farg, *args):
    print("formal arg:", farg)
    for arg in args:
        print("another arg:", arg)


print('test - 1')
test_var_args(1, "two", 3)



def test_var_kwargs(farg, **kwargs):
    print("formal arg:", farg)
    for key in kwargs:
        print("another keyword arg: %s: %s" % (key, kwargs[key]))
    
    print('\ntest - 2b')
    print('kwargs["myarg2"]:',kwargs['myarg2'])
    print('kwargs["myarg3"]:',kwargs['myarg3'])


print('\n\ntest - 2a')
test_var_kwargs(farg=1, myarg2="two", myarg3=3)